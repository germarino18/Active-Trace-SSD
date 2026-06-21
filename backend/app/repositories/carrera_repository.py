import uuid

from sqlalchemy import or_, select

from app.models.carrera import Carrera
from app.repositories.base import BaseRepository


class CarreraRepository(BaseRepository[Carrera]):
    def __init__(self, session, tenant_id: uuid.UUID | None = None):
        super().__init__(model=Carrera, session=session, tenant_id=tenant_id)

    async def find_by_codigo(
        self, tenant_id: uuid.UUID, codigo: str
    ) -> Carrera | None:
        query = select(self.model).where(
            self.model.tenant_id == tenant_id,
            self.model.codigo == codigo,
        )
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def find_all_filtered(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        activa: bool | None = None,
        q: str | None = None,
    ) -> list[Carrera]:
        query = select(self.model)
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)

        if activa is not None:
            query = query.where(self.model.estado == ("Activa" if activa else "Inactiva"))

        if q:
            query = query.where(
                self.model.nombre.ilike(f"%{q}%") | self.model.codigo.ilike(f"%{q}%")
            )

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())
