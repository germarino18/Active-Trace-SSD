"""Repository for SalarioPlus entity."""

import uuid
from datetime import date

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.salario_plus import SalarioPlus
from app.repositories.base import BaseRepository


class SalarioPlusRepository(BaseRepository[SalarioPlus]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID | None = None):
        super().__init__(model=SalarioPlus, session=session, tenant_id=tenant_id)

    async def find_vigentes_en(
        self, grupo: str, rol: str, fecha: date,
    ) -> list[SalarioPlus]:
        query = select(self.model).where(
            self.model.grupo == grupo,
            self.model.rol == rol,
            self.model.desde <= fecha,
            (self.model.hasta.is_(None)) | (self.model.hasta >= fecha),
        )
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def find_by_grupo_rol(
        self, grupo: str | None = None, rol: str | None = None,
    ) -> list[SalarioPlus]:
        query = select(self.model)
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        if grupo:
            query = query.where(self.model.grupo == grupo)
        if rol:
            query = query.where(self.model.rol == rol)
        query = query.order_by(self.model.grupo, self.model.rol, self.model.desde.desc())
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def check_solapamiento(
        self,
        grupo: str,
        rol: str,
        desde: date,
        hasta: date | None,
        exclude_id: uuid.UUID | None = None,
    ) -> bool:
        query = select(self.model).where(
            self.model.grupo == grupo,
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
