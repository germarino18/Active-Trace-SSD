"""Dependency guards for fine-grained permission checks.

Usage:
    @router.get(
        "/calificaciones",
        dependencies=[Depends(require_permission(Perm.CALIFICACIONES_IMPORTAR))],
    )
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.core.dependencies import get_db
from app.core.exceptions import ForbiddenException
from app.schemas.auth import CurrentUser
from app.services.permission_service import PermissionResolver


def require_permission(permiso: str):
    """Factory that returns a FastAPI dependency guard.

    Args:
        permiso: Permission string (e.g. \"calificaciones:importar\").

    Raises:
        ForbiddenException if the current user lacks the permission.
    """
    async def _dependency(
        current_user: CurrentUser = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> None:
        resolver = PermissionResolver(session=db)
        permissions = await resolver.get_effective_permissions(
            current_user.tenant_id, current_user.roles
        )
        if permiso not in permissions:
            raise ForbiddenException(action=permiso)

    return _dependency
