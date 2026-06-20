"""Repository for Actividad model (C-25)."""

import uuid

from sqlalchemy import select

from app.models.actividad import Actividad
from app.repositories.base import BaseRepository


class ActividadRepository(BaseRepository[Actividad]):
    def __init__(self, session, tenant_id: uuid.UUID | None = None):
        super().__init__(model=Actividad, session=session, tenant_id=tenant_id)

    async def find_by_dictado(self, dictado_id: uuid.UUID) -> list[Actividad]:
        """Return all non-deleted Actividades for a dictado, scoped to tenant."""
        query = select(self.model).where(
            self.model.dictado_id == dictado_id,
        )
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())
