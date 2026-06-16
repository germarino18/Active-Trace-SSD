"""Repository for Liquidacion entity."""

import uuid

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.liquidacion import EstadoLiquidacion, Liquidacion
from app.repositories.base import BaseRepository


class LiquidacionRepository(BaseRepository[Liquidacion]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID | None = None):
        super().__init__(model=Liquidacion, session=session, tenant_id=tenant_id)

    async def find_by_periodo(
        self, periodo: str, cohorte_id: uuid.UUID,
    ) -> list[Liquidacion]:
        query = select(self.model).where(
            self.model.periodo == periodo,
            self.model.cohorte_id == cohorte_id,
        )
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def find_by_usuario_periodo(
        self, usuario_id: uuid.UUID, periodo: str,
    ) -> Liquidacion | None:
        query = select(self.model).where(
            self.model.usuario_id == usuario_id,
            self.model.periodo == periodo,
        )
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def find_historial(
        self,
        cohorte_id: uuid.UUID | None = None,
        desde: str | None = None,
        hasta: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Liquidacion]:
        query = select(self.model).where(
            self.model.estado == EstadoLiquidacion.CERRADA.value,
        )
        query = self._apply_tenant_scope(query)
        if cohorte_id:
            query = query.where(self.model.cohorte_id == cohorte_id)
        if desde:
            query = query.where(self.model.periodo >= desde)
        if hasta:
            query = query.where(self.model.periodo <= hasta)
        query = query.order_by(self.model.periodo.desc(), self.model.usuario_id)
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def find_abiertas_por_periodo(
        self, periodo: str, cohorte_id: uuid.UUID,
    ) -> list[Liquidacion]:
        query = select(self.model).where(
            self.model.periodo == periodo,
            self.model.cohorte_id == cohorte_id,
            self.model.estado == EstadoLiquidacion.ABIERTA.value,
        )
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())
