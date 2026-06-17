"""Repository for MateriaClavePlus entity."""

import uuid
from datetime import date

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.materia_clave_plus import MateriaClavePlus
from app.repositories.base import BaseRepository


class MateriaClavePlusRepository(BaseRepository[MateriaClavePlus]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID | None = None):
        super().__init__(model=MateriaClavePlus, session=session, tenant_id=tenant_id)

    async def find_vigente_para_materia(
        self, materia_id: uuid.UUID, fecha: date,
    ) -> MateriaClavePlus | None:
        query = select(self.model).where(
            self.model.materia_id == materia_id,
            self.model.desde <= fecha,
            (self.model.hasta.is_(None)) | (self.model.hasta >= fecha),
        )
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        query = query.order_by(self.model.desde.desc()).limit(1)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def find_by_materia(
        self, materia_id: uuid.UUID,
    ) -> list[MateriaClavePlus]:
        query = select(self.model).where(self.model.materia_id == materia_id)
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def check_solapamiento(
        self,
        materia_id: uuid.UUID,
        desde: date,
        hasta: date | None,
        exclude_id: uuid.UUID | None = None,
    ) -> bool:
        query = select(self.model).where(
            self.model.materia_id == materia_id,
            self.model.desde <= (hasta or date(9999, 12, 31)),
            (self.model.hasta.is_(None)) | (self.model.hasta >= desde),
        )
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        if exclude_id:
            query = query.where(self.model.id != exclude_id)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none() is not None
