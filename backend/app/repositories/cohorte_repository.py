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
