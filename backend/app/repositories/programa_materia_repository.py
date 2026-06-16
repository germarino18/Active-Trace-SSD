import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.programa_materia import ProgramaMateria
from app.repositories.base import BaseRepository


class ProgramaMateriaRepository(BaseRepository[ProgramaMateria]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID | None = None):
        super().__init__(model=ProgramaMateria, session=session, tenant_id=tenant_id)

    async def find_by_dictado(self, dictado_id: uuid.UUID) -> ProgramaMateria | None:
        query = select(self.model).where(self.model.dictado_id == dictado_id)
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def exists_by_dictado(self, dictado_id: uuid.UUID) -> bool:
        return (await self.find_by_dictado(dictado_id)) is not None
