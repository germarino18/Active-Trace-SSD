import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evaluacion_materia import EvaluacionMateria
from app.repositories.base import BaseRepository


class EvaluacionMateriaRepository(BaseRepository[EvaluacionMateria]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID | None = None):
        super().__init__(model=EvaluacionMateria, session=session, tenant_id=tenant_id)

    async def list_by_tenant(
        self,
        *,
        materia_id: uuid.UUID | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[EvaluacionMateria]:
        query = select(self.model)
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        if materia_id is not None:
            query = query.where(self.model.materia_id == materia_id)
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())
