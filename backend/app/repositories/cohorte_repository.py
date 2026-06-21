import uuid

from sqlalchemy import select

from app.models.cohorte import Cohorte
from app.repositories.base import BaseRepository


class CohorteRepository(BaseRepository[Cohorte]):
    def __init__(self, session, tenant_id: uuid.UUID | None = None):
        super().__init__(model=Cohorte, session=session, tenant_id=tenant_id)

    async def find_by_nombre(
        self, tenant_id: uuid.UUID, carrera_id: uuid.UUID, nombre: str
    ) -> Cohorte | None:
        query = select(self.model).where(
            self.model.tenant_id == tenant_id,
            self.model.carrera_id == carrera_id,
            self.model.nombre == nombre,
        )
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def find_open_by_carrera(self, carrera_id: uuid.UUID) -> list[Cohorte]:
        query = select(self.model).where(
            self.model.carrera_id == carrera_id,
            self.model.vig_hasta.is_(None),
        )
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def find_all_filtered(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        activa: bool | None = None,
        q: str | None = None,
    ) -> list[Cohorte]:
        query = select(self.model)
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)

        if activa is not None:
            query = query.where(self.model.estado == ("Activa" if activa else "Inactiva"))

        if q:
            query = query.where(self.model.nombre.ilike(f"%{q}%"))

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())
