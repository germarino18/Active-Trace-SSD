import uuid

from sqlalchemy import select

from app.models.permiso import Permiso
from app.repositories.base import BaseRepository


class PermisoRepository(BaseRepository[Permiso]):
    def __init__(self, session, tenant_id: uuid.UUID | None = None):
        super().__init__(model=Permiso, session=session, tenant_id=tenant_id)

    async def find_by_codigo(
        self, tenant_id: uuid.UUID, codigo: str
    ) -> Permiso | None:
        query = select(self.model).where(
            self.model.tenant_id == tenant_id,
            self.model.codigo == codigo,
        )
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def find_by_modulo(
        self, tenant_id: uuid.UUID, modulo: str
    ) -> list[Permiso]:
        query = select(self.model).where(
            self.model.tenant_id == tenant_id,
            self.model.modulo == modulo,
        )
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())
