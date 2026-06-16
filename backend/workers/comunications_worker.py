"""Async worker for the communications queue.

Consumes Comunicacion records in Pendiente state and dispatches them.
Uses database-as-queue pattern (no external broker) for MVP simplicity.

Run with: python -m workers.comunications_worker
"""

import asyncio
import json
import logging
import os
import signal
import sys
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import Settings
from app.core.logging import JSONFormatter, setup_logging
from app.core.state_machine import StateMachine, TransitionError
from app.models.comunicacion import ComunicacionEstado
from app.repositories.comunicacion_repository import ComunicacionRepository

logger = logging.getLogger("comunications-worker")
settings = Settings()


class CommunicationsWorker:
    POLL_INTERVAL = int(os.getenv("WORKER_POLL_INTERVAL", "10"))
    ENVIANDO_TIMEOUT_MINUTES = int(os.getenv("WORKER_ENVIANDO_TIMEOUT", "5"))
    MAX_RETRIES = int(os.getenv("WORKER_MAX_RETRIES", "3"))

    def __init__(self) -> None:
        self.engine = create_async_engine(settings.database_url, echo=False)
        self.session_factory = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        self._shutdown_event = asyncio.Event()

        self._estados = ComunicacionEstado
        self._sm = StateMachine(
            state_enum=ComunicacionEstado,
            initial=ComunicacionEstado.PENDIENTE,
            transitions={
                ComunicacionEstado.PENDIENTE: [
                    ComunicacionEstado.ENVIANDO,
                    ComunicacionEstado.CANCELADO,
                ],
                ComunicacionEstado.ENVIANDO: [
                    ComunicacionEstado.ENVIADO,
                    ComunicacionEstado.ERROR,
                    ComunicacionEstado.PENDIENTE,
                ],
            },
        )

    async def run(self) -> None:
        logger.info(
            "worker_started",
            extra={
                "extra_fields": {
                    "poll_interval_s": self.POLL_INTERVAL,
                    "enviando_timeout_min": self.ENVIANDO_TIMEOUT_MINUTES,
                    "max_retries": self.MAX_RETRIES,
                }
            },
        )
        try:
            while not self._shutdown_event.is_set():
                try:
                    await self._process_pending()
                    await self._process_stuck()
                except Exception:
                    logger.exception("worker_cycle_error")
                await asyncio.sleep(self.POLL_INTERVAL)
        finally:
            await self.engine.dispose()
            logger.info("worker_stopped")

    async def _process_pending(self) -> None:
        async with self.session_factory() as session:
            repo = ComunicacionRepository(session, tenant_id=None)
            pendientes = await repo.get_pendientes()

            if not pendientes:
                return

            logger.info(
                "pending_found",
                extra={"extra_fields": {"count": len(pendientes)}},
            )

            for com in pendientes:
                try:
                    self._sm.validate_transition(
                        ComunicacionEstado.PENDIENTE,
                        ComunicacionEstado.ENVIANDO,
                    )
                    com.estado = ComunicacionEstado.ENVIANDO.value
                    await session.flush()

                    await self._dispatch(com)

                    self._sm.validate_transition(
                        ComunicacionEstado.ENVIANDO,
                        ComunicacionEstado.ENVIADO,
                    )
                    com.estado = ComunicacionEstado.ENVIADO.value
                    com.enviado_at = datetime.now(UTC)
                    await session.flush()
                    await session.commit()

                    logger.info(
                        "comunicacion_enviada",
                        extra={
                            "extra_fields": {
                                "id": str(com.id),
                                "lote_id": str(com.lote_id),
                                "materia_id": str(com.materia_id),
                                "tenant_id": str(com.tenant_id),
                            }
                        },
                    )

                except TransitionError as exc:
                    logger.warning(
                        "comunicacion_transition_invalid",
                        extra={
                            "extra_fields": {
                                "id": str(com.id),
                                "from_state": com.estado,
                                "to_state": ComunicacionEstado.ENVIANDO.value,
                                "error": str(exc),
                            }
                        },
                    )
                    await session.rollback()
                except Exception:
                    logger.exception(
                        "comunicacion_dispatch_error",
                        extra={
                            "extra_fields": {
                                "id": str(com.id),
                                "lote_id": str(com.lote_id),
                            }
                        },
                    )
                    await session.rollback()

    async def _dispatch(self, com) -> None:
        logger.info(
            "dispatching",
            extra={
                "extra_fields": {
                    "id": str(com.id),
                    "destinatario_hash": com.destinatario_hash,
                    "asunto": com.asunto,
                }
            },
        )
        await asyncio.sleep(0.1)

    async def _process_stuck(self) -> None:
        async with self.session_factory() as session:
            repo = ComunicacionRepository(session, tenant_id=None)
            stuck = await repo.get_stuck_enviando(
                timeout_minutes=self.ENVIANDO_TIMEOUT_MINUTES
            )

            if not stuck:
                return

            logger.warning(
                "stuck_found",
                extra={"extra_fields": {"count": len(stuck)}},
            )

            for com in stuck:
                com.reintentos = (com.reintentos or 0) + 1

                if com.reintentos >= self.MAX_RETRIES:
                    self._sm.validate_transition(
                        ComunicacionEstado.ENVIANDO,
                        ComunicacionEstado.ERROR,
                    )
                    com.estado = ComunicacionEstado.ERROR.value
                    logger.error(
                        "comunicacion_max_retries_exceeded",
                        extra={
                            "extra_fields": {
                                "id": str(com.id),
                                "reintentos": com.reintentos,
                            }
                        },
                    )
                else:
                    self._sm.validate_transition(
                        ComunicacionEstado.ENVIANDO,
                        ComunicacionEstado.PENDIENTE,
                    )
                    com.estado = ComunicacionEstado.PENDIENTE.value
                    logger.info(
                        "comunicacion_retry",
                        extra={
                            "extra_fields": {
                                "id": str(com.id),
                                "reintentos": com.reintentos,
                                "max_retries": self.MAX_RETRIES,
                            }
                        },
                    )

                await session.flush()
                await session.commit()

    def shutdown(self) -> None:
        logger.info("shutdown_requested")
        self._shutdown_event.set()


def _setup_signal_handlers(worker: CommunicationsWorker) -> None:
    loop = asyncio.get_event_loop()

    def _signal_handler() -> None:
        worker.shutdown()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _signal_handler)
        except NotImplementedError:
            logger.warning(
                "signal_handler_not_supported",
                extra={"extra_fields": {"signal": sig.name}},
            )


def main() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    for h in root.handlers[:]:
        root.removeHandler(h)
    root.addHandler(handler)

    worker = CommunicationsWorker()
    _setup_signal_handlers(worker)

    try:
        asyncio.run(worker.run())
    except KeyboardInterrupt:
        worker.shutdown()


if __name__ == "__main__":
    main()
