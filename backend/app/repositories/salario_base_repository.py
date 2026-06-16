"""Repository for SalarioBase entity."""

import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.salario_base import SalarioBase
from app.repositories.base import BaseRepository


class SalarioBaseRepository(BaseRepository[SalarioBase]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID | None = None):
        super().__init__(model=SalarioBase, session=session, tenant_id=tenant_id)

    async def find_vigente_en(self, rol: str, fecha: date) -> SalarioBase | None:
        query = select(self.model).where(
            self.model.rol == rol,
            self.model.desde <= fecha,
            (self.model.hasta.is_(None)) | (self.model.hasta >= fecha),
        )
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        query = query.order_by(self.model.desde.desc()).limit(1)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def find_all_by_rol(self, rol: str | None = None) -> list[SalarioBase]:
        query = select(self.model)
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        if rol:
            query = query.where(self.model.rol == rol)
        query = query.order_by(self.model.rol, self.model.desde.desc())
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def check_solapamiento(
        self,
        rol: str,
        desde: date,
        hasta: date | None,
        exclude_id: uuid.UUID | None = None,
    ) -> bool:
        query = select(self.model).where(
            self.model.rol == rol,
            self.model.desde <= (hasta or date(9999, 12, 31)),
            (self.model.hasta.is_(None)) | (self.model.hasta >= desde),
        )
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        if exclude_id:
            query = query.where(self.model.id != exclude_id)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none() is not None
