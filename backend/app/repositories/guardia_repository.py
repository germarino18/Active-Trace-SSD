import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.guardia import Guardia
from app.repositories.base import BaseRepository


class GuardiaRepository(BaseRepository[Guardia]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID | None = None):
        super().__init__(model=Guardia, session=session, tenant_id=tenant_id)

    async def list_by_tenant(
        self,
        *,
        dictado_id: uuid.UUID | None = None,
        asignacion_id: uuid.UUID | None = None,
        estado: str | None = None,
        dia: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Guardia]:
        query = select(self.model)
        query = self._apply_tenant_scope(query)

        filters = []
        if dictado_id is not None:
            filters.append(self.model.dictado_id == dictado_id)
        if asignacion_id is not None:
            filters.append(self.model.asignacion_id == asignacion_id)
        if estado is not None:
            filters.append(self.model.estado == estado)
        if dia is not None:
            filters.append(self.model.dia == dia)

        if filters:
            query = query.where(filters[0])
            for f in filters[1:]:
                query = query.where(f)

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def list_by_asignacion(
        self, asignacion_id: uuid.UUID
    ) -> list[Guardia]:
        return await self.find_by(asignacion_id=asignacion_id)

    async def list_for_export(
        self,
        *,
        dictado_id: uuid.UUID | None = None,
        asignacion_id: uuid.UUID | None = None,
        estado: str | None = None,
    ) -> list[Guardia]:
        """List guardias for export (no pagination)."""
        query = select(self.model)
        query = self._apply_tenant_scope(query)

        if dictado_id is not None:
            query = query.where(self.model.dictado_id == dictado_id)
        if asignacion_id is not None:
            query = query.where(self.model.asignacion_id == asignacion_id)
        if estado is not None:
            query = query.where(self.model.estado == estado)

        result = await self.session.execute(query)
        return list(result.unique().scalars().all())
