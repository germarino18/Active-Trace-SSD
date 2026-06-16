import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fecha_academica import FechaAcademica
from app.repositories.base import BaseRepository


class FechaAcademicaRepository(BaseRepository[FechaAcademica]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID | None = None):
        super().__init__(model=FechaAcademica, session=session, tenant_id=tenant_id)

    async def find_by_dictado_periodo(
        self,
        dictado_id: uuid.UUID,
        periodo: str | None = None,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[FechaAcademica]:
        query = select(self.model).where(self.model.dictado_id == dictado_id)
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        if periodo is not None:
            query = query.where(self.model.periodo == periodo)
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def find_calendar(
        self,
        dictado_id: uuid.UUID,
        periodo: str | None = None,
    ) -> list[FechaAcademica]:
        query = select(self.model).where(self.model.dictado_id == dictado_id)
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        if periodo is not None:
            query = query.where(self.model.periodo == periodo)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def exists_by_dictado_tipo_numero(
        self,
        dictado_id: uuid.UUID,
        tipo: str,
        numero: int,
    ) -> bool:
        query = (
            select(self.model)
            .where(self.model.dictado_id == dictado_id)
            .where(self.model.tipo == tipo)
            .where(self.model.numero == numero)
        )
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none() is not None
