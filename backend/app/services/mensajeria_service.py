from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.hilo_conversacion import HiloConversacion
from app.models.usuario import Usuario
from app.repositories.base import BaseRepository
from app.repositories.hilo_repository import HiloRepository
from app.repositories.mensaje_repository import MensajeRepository
from app.schemas.mensajeria import HiloResponse, MensajeResponse


class MensajeriaService:
    """Servicio para la bandeja de mensajería interna."""

    def __init__(self, db: AsyncSession, tenant_id: UUID):
        self._db = db
        self._hilo_repo = HiloRepository(session=db, tenant_id=tenant_id)
        self._mensaje_repo = MensajeRepository(session=db, tenant_id=tenant_id)
        self._usuario_repo = BaseRepository(
            model=Usuario,
            session=db,
            tenant_id=tenant_id,
        )

    async def _get_usuario_nombre(self, usuario_id: UUID) -> str:
        """Resuelve el nombre de un usuario."""
        usuarios = await self._usuario_repo.find_by(id=usuario_id)
        if usuarios:
            u = usuarios[0]
            return f"{u.nombre} {u.apellidos}".strip() or u.nombre
        return ""

    async def list_hilos(self, usuario_id: UUID) -> list[HiloResponse]:
        """Retorna los hilos del usuario con último mensaje y estado no_leido."""
        hilos = await self._hilo_repo.list_by_participante(usuario_id)
        result: list[HiloResponse] = []

        for hilo in hilos:
            ultimo = await self._mensaje_repo.get_ultimo_mensaje(hilo.id)
            if ultimo is None:
                continue

            otro_id = await self._hilo_repo.obtener_otro_participante(hilo.id, usuario_id)
            remitente_nombre = await self._get_usuario_nombre(otro_id or ultimo.remitente_id)

            # Determinar si hay mensajes no leídos
            from app.models.hilo_participante import HiloParticipante
            from sqlalchemy import select

            query = select(HiloParticipante).where(
                HiloParticipante.hilo_id == hilo.id,
                HiloParticipante.usuario_id == usuario_id,
            )
            row = await self._db.execute(query)
            participante = row.scalar_one_or_none()
            ultima_visto = participante.ultima_visto if participante else None

            no_leido = await self._mensaje_repo.count_no_leidos(
                hilo.id, usuario_id, ultima_visto
            )
            # Si ultima_visto es None y hay al menos un mensaje de otro, no_leido > 0

            result.append(HiloResponse(
                id=hilo.id,
                remitente_id=otro_id or ultimo.remitente_id,
                remitente_nombre=remitente_nombre,
                asunto=hilo.asunto,
                ultimo_mensaje=ultimo.contenido[:120] + ("..." if len(ultimo.contenido) > 120 else ""),
                ultima_fecha=ultimo.created_at,
                no_leido=no_leido > 0,
            ))

        # Ordenar por ultima_fecha descendente
        result.sort(key=lambda h: h.ultima_fecha, reverse=True)
        return result

    async def get_hilo(self, hilo_id: UUID, usuario_id: UUID) -> list[MensajeResponse]:
        """Retorna los mensajes de un hilo, validando pertenencia.

        Raises NotFoundException si el hilo no existe o el usuario no es participante.
        """
        hilo = await self._hilo_repo.get_by_id(hilo_id)
        if hilo is None:
            raise NotFoundException(resource="Hilo", id=hilo_id)

        if not await self._hilo_repo.es_participante(hilo_id, usuario_id):
            raise NotFoundException(resource="Hilo", id=hilo_id)

        # Marcar como visto
        await self._hilo_repo.actualizar_visto(hilo_id, usuario_id)

        mensajes = await self._mensaje_repo.list_by_hilo(hilo_id)
        result: list[MensajeResponse] = []

        for msg in mensajes:
            remitente_nombre = await self._get_usuario_nombre(msg.remitente_id)
            result.append(MensajeResponse(
                id=msg.id,
                remitente_id=msg.remitente_id,
                remitente_nombre=remitente_nombre,
                contenido=msg.contenido,
                fecha_hora=msg.created_at,
            ))

        return result

    async def responder(
        self,
        hilo_id: UUID,
        usuario_id: UUID,
        contenido: str,
    ) -> MensajeResponse:
        """Responde en un hilo existente.

        Raises NotFoundException si el hilo no existe o el usuario no es participante.
        """
        hilo = await self._hilo_repo.get_by_id(hilo_id)
        if hilo is None:
            raise NotFoundException(resource="Hilo", id=hilo_id)

        if not await self._hilo_repo.es_participante(hilo_id, usuario_id):
            raise NotFoundException(resource="Hilo", id=hilo_id)

        # Crear el mensaje
        mensaje = await self._mensaje_repo.create({
            "hilo_id": hilo_id,
            "remitente_id": usuario_id,
            "contenido": contenido,
        })

        # Actualizar visto del remitente (ya lo vio porque lo está escribiendo)
        await self._hilo_repo.actualizar_visto(hilo_id, usuario_id)

        remitente_nombre = await self._get_usuario_nombre(usuario_id)

        return MensajeResponse(
            id=mensaje.id,
            remitente_id=mensaje.remitente_id,
            remitente_nombre=remitente_nombre,
            contenido=mensaje.contenido,
            fecha_hora=mensaje.created_at,
        )
