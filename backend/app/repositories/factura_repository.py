"""Repository for Factura entity."""

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.factura import Factura
from app.repositories.base import BaseRepository


class FacturaRepository(BaseRepository[Factura]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID | None = None):
        super().__init__(model=Factura, session=session, tenant_id=tenant_id)

    async def find_by_usuario(
        self, usuario_id: uuid.UUID,
    ) -> list[Factura]:
        query = select(self.model).where(self.model.usuario_id == usuario_id)
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        query = query.order_by(self.model.cargada_at.desc())
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def find_by_periodo(self, periodo: str) -> list[Factura]:
        query = select(self.model).where(self.model.periodo == periodo)
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def find_by_estado(self, estado: str) -> list[Factura]:
        query = select(self.model).where(self.model.estado == estado)
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def find_filtered(
        self,
        usuario_id: uuid.UUID | None = None,
        periodo: str | None = None,
        estado: str | None = None,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Factura]:
        query = select(self.model)
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        if usuario_id:
            query = query.where(self.model.usuario_id == usuario_id)
        if periodo:
            query = query.where(self.model.periodo == periodo)
        if estado:
            query = query.where(self.model.estado == estado)
        if desde:
            query = query.where(self.model.cargada_at >= desde)
        if hasta:
            query = query.where(self.model.cargada_at <= hasta)
        query = query.order_by(self.model.cargada_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())
