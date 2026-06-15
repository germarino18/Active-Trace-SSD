import uuid

from sqlalchemy import delete, func, select

from app.models.entrada_padron import EntradaPadron
from app.repositories.base import BaseRepository


class EntradaPadronRepository(BaseRepository[EntradaPadron]):
    def __init__(self, session, tenant_id: uuid.UUID | None = None):
        super().__init__(model=EntradaPadron, session=session, tenant_id=tenant_id)

    async def bulk_create(self, entries: list[dict]) -> list[EntradaPadron]:
        tenant_id = self._get_effective_tenant_id()
        instances = []
        for data in entries:
            row_data = dict(data)
            if tenant_id is not None:
                row_data.setdefault("tenant_id", tenant_id)
            instance = EntradaPadron(**row_data)
            self.session.add(instance)
            instances.append(instance)
        await self.session.flush()
        for instance in instances:
            await self.session.refresh(instance)
        return instances

    async def find_by_version(self, version_id: uuid.UUID) -> list[EntradaPadron]:
        query = select(self.model).where(
            self.model.version_id == version_id,
        )
        query = self._apply_tenant_scope(query)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def count_by_version(self, version_id: uuid.UUID) -> int:
        query = select(func.count()).select_from(self.model).where(
            self.model.version_id == version_id,
        )
        query = self._apply_tenant_scope(query)
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def delete_by_version(self, version_id: uuid.UUID) -> int:
        stmt = (
            delete(self.model)
            .where(self.model.version_id == version_id)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount
