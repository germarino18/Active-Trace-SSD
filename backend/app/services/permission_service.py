import uuid
from contextvars import ContextVar
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.rol_permiso_repository import RolPermisoRepository


@dataclass
class PermissionCache:
    effective_permissions: set[str] = field(default_factory=set)
    metadata: dict[str, bool] = field(default_factory=dict)


_permission_cache: ContextVar[PermissionCache | None] = ContextVar(
    "_permission_cache", default=None
)


class PermissionResolver:
    """Resolves effective permissions for a user's roles, cached per request.

    Usage:
        resolver = PermissionResolver(session)
        perms = await resolver.get_effective_permissions(tenant_id, roles)
        meta = await resolver.get_permission_metadata(tenant_id, roles)
    """

    def __init__(self, session: AsyncSession):
        self._session = session
        self._repo = RolPermisoRepository(session=session)

    async def get_effective_permissions(
        self, tenant_id: uuid.UUID, role_codes: list[str]
    ) -> set[str]:
        cache = await self._load_cache(tenant_id, role_codes)
        return cache.effective_permissions

    async def get_permission_metadata(
        self, tenant_id: uuid.UUID, role_codes: list[str]
    ) -> dict[str, bool]:
        cache = await self._load_cache(tenant_id, role_codes)
        return cache.metadata

    async def _load_cache(
        self, tenant_id: uuid.UUID, role_codes: list[str]
    ) -> PermissionCache:
        existing = _permission_cache.get()
        if existing is not None:
            return existing

        rows = await self._repo.find_permisos_for_roles(tenant_id, role_codes)
        perms = set()
        meta: dict[str, bool] = {}
        for codigo, es_propio in rows:
            perms.add(codigo)
            meta[codigo] = es_propio

        cache = PermissionCache(effective_permissions=perms, metadata=meta)
        _permission_cache.set(cache)
        return cache

    @staticmethod
    def clear_cache():
        _permission_cache.set(None)
