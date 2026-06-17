"""Repository for ClavePlus entity."""

import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clave_plus import ClavePlus
from app.repositories.base import BaseRepository


class ClavePlusRepository(BaseRepository[ClavePlus]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID | None = None):
        super().__init__(model=ClavePlus, session=session, tenant_id=tenant_id)

    async def find_by_codigo(self, codigo: str) -> ClavePlus | None:
        query = select(self.model).where(self.model.codigo == codigo)
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def find_vigentes_en(self, fecha: date) -> list[ClavePlus]:
        query = select(self.model).where(
            self.model.desde <= fecha,
            (self.model.hasta.is_(None)) | (self.model.hasta >= fecha),
        )
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())
