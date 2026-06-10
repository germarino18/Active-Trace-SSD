"""RESERVADO para ADR-003: worker de cola de comunicaciones.

Placeholder no-op. La tecnología real de la cola (asyncio propio, ARQ, Celery)
se define en ADR-003 al construir el módulo de comunicaciones.
"""

import asyncio
import logging

logger = logging.getLogger(__name__)


async def main():
    logger.info("Worker started (no-op placeholder)")
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
