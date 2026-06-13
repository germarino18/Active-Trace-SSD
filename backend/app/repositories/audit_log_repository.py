import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.repositories.base import BaseRepository


class AuditLogRepository:
    """Append-only repository for `AuditLog` (D2).

    Composes a `BaseRepository[AuditLog]` internally but exposes ONLY
    `create` and read/list operations. `update`/`soft_delete`/`hard_delete`
    are intentionally NOT exposed on this class — the audit trail is
    immutable at the application layer (the DB-level trigger from
    migration 004 enforces it independently, see D2).
    """

    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID | None = None):
        self._base = BaseRepository(model=AuditLog, session=session, tenant_id=tenant_id)

    async def create(self, data: dict) -> AuditLog:
        return await self._base.create(data)

    async def find_by_id(self, id: uuid.UUID) -> AuditLog | None:
        return await self._base.find_by_id(id)

    async def find_all(self, *, skip: int = 0, limit: int = 100) -> list[AuditLog]:
        return await self._base.find_all(skip=skip, limit=limit)

    async def find_by(self, **filters) -> list[AuditLog]:
        return await self._base.find_by(**filters)
