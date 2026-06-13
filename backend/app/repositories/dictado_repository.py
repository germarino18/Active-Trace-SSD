import uuid

from sqlalchemy import select

from app.models.dictado import Dictado
from app.repositories.base import BaseRepository


class DictadoRepository(BaseRepository[Dictado]):
    def __init__(self, session, tenant_id: uuid.UUID | None = None):
        super().__init__(model=Dictado, session=session, tenant_id=tenant_id)

    async def find_by_terna(
        self,
        tenant_id: uuid.UUID,
        materia_id: uuid.UUID,
        carrera_id: uuid.UUID,
        cohorte_id: uuid.UUID,
    ) -> Dictado | None:
        query = select(self.model).where(
            self.model.tenant_id == tenant_id,
            self.model.materia_id == materia_id,
            self.model.carrera_id == carrera_id,
            self.model.cohorte_id == cohorte_id,
        )
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()
