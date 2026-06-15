import uuid

from sqlalchemy import delete, select, update

from app.models.version_padron import VersionPadron
from app.repositories.base import BaseRepository


class VersionPadronRepository(BaseRepository[VersionPadron]):
    def __init__(self, session, tenant_id: uuid.UUID | None = None):
        super().__init__(model=VersionPadron, session=session, tenant_id=tenant_id)

    async def find_active_by_dictado(self, dictado_id: uuid.UUID) -> VersionPadron | None:
        query = select(self.model).where(
            self.model.dictado_id == dictado_id,
            self.model.activa.is_(True),
        )
        query = self._apply_tenant_scope(query)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def find_by_dictado(self, dictado_id: uuid.UUID) -> list[VersionPadron]:
        query = select(self.model).where(
            self.model.dictado_id == dictado_id,
        )
        query = self._apply_tenant_scope(query)
        query = query.order_by(self.model.cargado_at.desc())
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def deactivate_version(self, version_id: uuid.UUID) -> VersionPadron:
        stmt = (
            update(self.model)
            .where(self.model.id == version_id)
            .values(activa=False)
        )
        await self.session.execute(stmt)
        await self.session.flush()
        found = await self.find_by_id(version_id)
        if found is None:
            raise ValueError(f"VersionPadron {version_id} not found after deactivate")
        return found

    async def delete_by_dictado_and_cargador(
        self, dictado_id: uuid.UUID, cargado_por: uuid.UUID
    ) -> int:
        stmt = (
            delete(self.model)
            .where(
                self.model.dictado_id == dictado_id,
                self.model.cargado_por == cargado_por,
            )
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount

    async def delete_all_by_dictado(self, dictado_id: uuid.UUID) -> int:
        stmt = (
            delete(self.model)
            .where(self.model.dictado_id == dictado_id)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount
