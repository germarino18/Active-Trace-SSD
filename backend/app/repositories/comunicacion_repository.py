import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comunicacion import Comunicacion, ComunicacionEstado
from app.repositories.base import BaseRepository


class ComunicacionRepository(BaseRepository[Comunicacion]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID | None = None):
        super().__init__(model=Comunicacion, session=session, tenant_id=tenant_id)

    async def get_by_lote(self, lote_id: uuid.UUID) -> list[Comunicacion]:
        query = select(self.model).where(self.model.lote_id == lote_id)
        query = self._apply_tenant_scope(query)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def get_pendientes(self, limit: int = 50) -> list[Comunicacion]:
        query = (
            select(self.model)
            .where(self.model.estado == ComunicacionEstado.PENDIENTE.value)
            .limit(limit)
        )
        query = self._apply_tenant_scope(query)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def get_stuck_enviando(self, timeout_minutes: int = 5) -> list[Comunicacion]:
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=timeout_minutes)
        query = (
            select(self.model)
            .where(
                self.model.estado == ComunicacionEstado.ENVIANDO.value,
                self.model.updated_at < cutoff,
                self.model.reintentos < 3,
            )
        )
        query = self._apply_tenant_scope(query)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def update_estado(
        self, id: uuid.UUID, estado: ComunicacionEstado, extra: dict | None = None
    ) -> Comunicacion:
        update_data: dict = {"estado": estado.value}
        if estado == ComunicacionEstado.ENVIADO:
            update_data["enviado_at"] = datetime.now(timezone.utc)
        if extra:
            update_data.update(extra)
        return await self.update(id, update_data)

    async def count_by_lote(self, lote_id: uuid.UUID) -> dict[str, int]:
        query = (
            select(self.model.estado, func.count(self.model.id))
            .where(self.model.lote_id == lote_id)
            .group_by(self.model.estado)
        )
        query = self._apply_tenant_scope(query)
        result = await self.session.execute(query)
        counts: dict[str, int] = {
            "total": 0,
            "Pendiente": 0,
            "Enviado": 0,
            "Error": 0,
            "Cancelado": 0,
        }
        for row in result:
            counts[str(row[0])] = row[1]
            counts["total"] += row[1]
        return counts

    async def get_pendientes_count(self) -> int:
        query = select(func.count(self.model.id)).where(
            self.model.estado == ComunicacionEstado.PENDIENTE.value
        )
        query = self._apply_tenant_scope(query)
        result = await self.session.execute(query)
        return result.scalar_one()
