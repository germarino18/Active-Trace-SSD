import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resultado_evaluacion import ResultadoEvaluacion
from app.repositories.base import BaseRepository


class ResultadoEvaluacionRepository(BaseRepository[ResultadoEvaluacion]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID | None = None):
        super().__init__(
            model=ResultadoEvaluacion, session=session, tenant_id=tenant_id
        )

    async def get_by_evaluacion_alumno(
        self, evaluacion_id: uuid.UUID, alumno_id: uuid.UUID
    ) -> ResultadoEvaluacion | None:
        query = select(self.model).where(
            self.model.evaluacion_id == evaluacion_id,
            self.model.alumno_id == alumno_id,
        )
        query = self._apply_tenant_scope(query)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def list_by_tenant(
        self,
        *,
        evaluacion_id: uuid.UUID | None = None,
        alumno_id: uuid.UUID | None = None,
        dictado_id: uuid.UUID | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ResultadoEvaluacion]:
        from app.models.evaluacion import Evaluacion

        query = (
            select(self.model)
            .join(Evaluacion, self.model.evaluacion_id == Evaluacion.id)
        )
        query = self._apply_tenant_scope(query)

        filters = []
        if evaluacion_id is not None:
            filters.append(self.model.evaluacion_id == evaluacion_id)
        if alumno_id is not None:
            filters.append(self.model.alumno_id == alumno_id)
        if dictado_id is not None:
            filters.append(Evaluacion.dictado_id == dictado_id)

        for f in filters:
            query = query.where(f)

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())
