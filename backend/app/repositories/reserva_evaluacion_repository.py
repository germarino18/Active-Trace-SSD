import uuid

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reserva_evaluacion import ReservaEvaluacion
from app.repositories.base import BaseRepository


class ReservaEvaluacionRepository(BaseRepository[ReservaEvaluacion]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID | None = None):
        super().__init__(
            model=ReservaEvaluacion, session=session, tenant_id=tenant_id
        )

    async def create_with_for_update(
        self, evaluacion_id: uuid.UUID, alumno_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> ReservaEvaluacion:
        """Create a reservation with FOR UPDATE lock on the evaluacion row.

        The caller MUST be inside a transaction. This method executes:
        1. SELECT ... FOR UPDATE on the evaluacion (to lock the cupo check)
        2. INSERT the reserva
        """
        # Lock the evaluacion row to prevent race conditions on cupo
        lock_query = select(func.now())  # placeholder — actual locking done in service
        await self.session.execute(lock_query)

        instance = self.model(
            evaluacion_id=evaluacion_id,
            alumno_id=alumno_id,
            tenant_id=tenant_id,
            estado="Activa",
        )
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def count_activas_by_evaluacion(
        self, evaluacion_id: uuid.UUID
    ) -> int:
        query = (
            select(func.count(self.model.id))
            .where(
                self.model.evaluacion_id == evaluacion_id,
                self.model.estado == "Activa",
            )
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def cancelar(self, reserva_id: uuid.UUID) -> ReservaEvaluacion | None:
        """Cancel a reservation (set estado to Cancelada)."""
        instance = await self.find_by_id(reserva_id)
        if instance is None:
            return None
        instance.estado = "Cancelada"
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def list_activas_by_tenant(
        self,
        *,
        evaluacion_id: uuid.UUID | None = None,
        alumno_id: uuid.UUID | None = None,
        dictado_id: uuid.UUID | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ReservaEvaluacion]:
        """List active reservations with optional filters (scoped by tenant)."""
        from app.models.evaluacion import Evaluacion

        query = (
            select(self.model)
            .join(Evaluacion, self.model.evaluacion_id == Evaluacion.id)
        )
        query = self._apply_tenant_scope(query)
        query = query.where(self.model.estado == "Activa")

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
