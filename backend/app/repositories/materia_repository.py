import uuid

from sqlalchemy import or_, select
from sqlalchemy.orm import joinedload

from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.materia import Materia
from app.repositories.base import BaseRepository


class MateriaRepository(BaseRepository[Materia]):
    def __init__(self, session, tenant_id: uuid.UUID | None = None):
        super().__init__(model=Materia, session=session, tenant_id=tenant_id)

    def _base_query(self):
        return select(self.model).options(
            joinedload(self.model.carrera).load_only(Carrera.nombre),
            joinedload(self.model.cohorte).load_only(Cohorte.nombre),
        )

    async def get_with_relations(self, id: uuid.UUID) -> Materia | None:
        """Fetch materia by id with carrera/cohorte relationships eagerly loaded."""
        return await self.find_by_id(id)

    async def find_by_id(self, id: uuid.UUID) -> Materia | None:
        query = self._base_query().where(self.model.id == id)
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def find_by_codigo(
        self, tenant_id: uuid.UUID, codigo: str
    ) -> Materia | None:
        query = self._base_query().where(
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
    ) -> list[Materia]:
        query = self._base_query()
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
