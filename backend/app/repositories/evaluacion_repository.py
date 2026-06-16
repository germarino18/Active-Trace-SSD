import uuid
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alumno_convocado import AlumnoConvocado
from app.models.evaluacion import Evaluacion
from app.models.reserva_evaluacion import ReservaEvaluacion
from app.models.resultado_evaluacion import ResultadoEvaluacion
from app.repositories.base import BaseRepository


class EvaluacionRepository(BaseRepository[Evaluacion]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID | None = None):
        super().__init__(model=Evaluacion, session=session, tenant_id=tenant_id)

    async def list_by_tenant(
        self,
        *,
        dictado_id: uuid.UUID | None = None,
        estado: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Evaluacion]:
        query = select(self.model)
        query = self._apply_tenant_scope(query)
        filters = []
        if dictado_id is not None:
            filters.append(self.model.dictado_id == dictado_id)
        if estado is not None:
            filters.append(self.model.estado == estado)
        for f in filters:
            query = query.where(f)
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def count_metricas(
        self,
    ) -> dict[str, int]:
        """Return panel metrics for the tenant scope."""
        # Total alumnos convocados en al menos una evaluacion
        convocados_query = (
            select(func.count(func.distinct(AlumnoConvocado.alumno_id)))
            .select_from(AlumnoConvocado)
            .join(Evaluacion, AlumnoConvocado.evaluacion_id == Evaluacion.id)
        )
        convocados_query = self._apply_tenant_scope(convocados_query)

        instancias_activas_query = select(func.count(self.model.id)).where(
            self.model.estado == "Activa"
        )
        instancias_activas_query = self._apply_tenant_scope(instancias_activas_query)

        reservas_activas_query = (
            select(func.count(ReservaEvaluacion.id))
            .select_from(ReservaEvaluacion)
            .join(Evaluacion, ReservaEvaluacion.evaluacion_id == Evaluacion.id)
            .where(ReservaEvaluacion.estado == "Activa")
        )
        reservas_activas_query = self._apply_tenant_scope(reservas_activas_query)

        notas_query = (
            select(func.count(ResultadoEvaluacion.id))
            .select_from(ResultadoEvaluacion)
            .join(Evaluacion, ResultadoEvaluacion.evaluacion_id == Evaluacion.id)
        )
        notas_query = self._apply_tenant_scope(notas_query)

        convocados = (await self.session.execute(convocados_query)).scalar() or 0
        instancias = (await self.session.execute(instancias_activas_query)).scalar() or 0
        reservas = (await self.session.execute(reservas_activas_query)).scalar() or 0
        notas = (await self.session.execute(notas_query)).scalar() or 0

        return {
            "total_alumnos_convocados": convocados,
            "instancias_activas": instancias,
            "reservas_activas": reservas,
            "notas_registradas": notas,
        }
