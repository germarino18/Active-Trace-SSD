import uuid

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alumno_convocado import AlumnoConvocado
from app.repositories.base import BaseRepository


class AlumnoConvocadoRepository(BaseRepository[AlumnoConvocado]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID | None = None):
        super().__init__(
            model=AlumnoConvocado, session=session, tenant_id=tenant_id
        )

    async def bulk_import(
        self, evaluacion_id: uuid.UUID, alumno_ids: list[uuid.UUID], tenant_id: uuid.UUID
    ) -> int:
        """Import alumnos idempotently (INSERT ON CONFLICT DO NOTHING).

        Returns the number of new rows inserted.
        """
        if not alumno_ids:
            return 0

        stmt = pg_insert(AlumnoConvocado).values(
            [
                {
                    "evaluacion_id": evaluacion_id,
                    "alumno_id": aid,
                    "tenant_id": tenant_id,
                }
                for aid in alumno_ids
            ]
        )
        stmt = stmt.on_conflict_do_nothing(
            constraint="uq_alumno_convocado_evaluacion_alumno"
        )
        result = await self.session.execute(stmt)
        return result.rowcount

    async def list_by_evaluacion(
        self, evaluacion_id: uuid.UUID
    ) -> list[AlumnoConvocado]:
        return await self.find_by(evaluacion_id=evaluacion_id)

    async def exists(
        self, evaluacion_id: uuid.UUID, alumno_id: uuid.UUID
    ) -> bool:
        query = select(self.model).where(
            self.model.evaluacion_id == evaluacion_id,
            self.model.alumno_id == alumno_id,
        )
        query = self._apply_tenant_scope(query)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none() is not None
