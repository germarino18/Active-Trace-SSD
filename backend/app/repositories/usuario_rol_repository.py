import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.usuario_rol import UsuarioRol
from app.repositories.base import BaseRepository


class UsuarioRolRepository(BaseRepository[UsuarioRol]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID | None = None):
        super().__init__(model=UsuarioRol, session=session, tenant_id=tenant_id)

    async def find_by_usuario(self, usuario_id: uuid.UUID) -> list[UsuarioRol]:
        query = select(self.model).where(self.model.usuario_id == usuario_id)
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def find_by_usuario_and_rol(
        self, usuario_id: uuid.UUID, rol_id: uuid.UUID
    ) -> UsuarioRol | None:
        query = select(self.model).where(
            self.model.usuario_id == usuario_id,
            self.model.rol_id == rol_id,
        )
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()
