from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.core.dependencies import get_db
from app.core.exceptions import NotFoundException
from app.core.permissions import Perm
from app.repositories.permiso_repository import PermisoRepository
from app.repositories.rol_permiso_repository import RolPermisoRepository
from app.repositories.rol_repository import RolRepository
from app.schemas.auth import CurrentUser
from app.schemas.permissions import (
    PermisoCreate,
    PermisoResponse,
    PermisoUpdate,
    RolCreate,
    RolPermisoCreate,
    RolResponse,
    RolUpdate,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])

# All admin endpoints require ESTRUCTURA_GESTIONAR
_admin_guard = [Depends(require_permission(Perm.ESTRUCTURA_GESTIONAR))]


# ── Roles CRUD ─────────────────────────────────────────────────────────


@router.get("/roles", response_model=list[RolResponse], dependencies=_admin_guard)
async def list_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = RolRepository(session=db, tenant_id=current_user.tenant_id)
    roles = await repo.find_all(skip=skip, limit=limit)
    return [_rol_to_response(r) for r in roles]


@router.post("/roles", response_model=RolResponse, status_code=201, dependencies=_admin_guard)
async def create_role(
    data: RolCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = RolRepository(session=db, tenant_id=current_user.tenant_id)
    role = await repo.create(data)
    return _rol_to_response(role)


@router.get("/roles/{rol_id}", response_model=RolResponse, dependencies=_admin_guard)
async def get_role(
    rol_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = RolRepository(session=db, tenant_id=current_user.tenant_id)
    role = await repo.find_by_id(rol_id)
    if role is None:
        raise NotFoundException(resource="Rol", id=rol_id)
    return _rol_to_response(role)


@router.put("/roles/{rol_id}", response_model=RolResponse, dependencies=_admin_guard)
async def update_role(
    rol_id: UUID,
    data: RolUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = RolRepository(session=db, tenant_id=current_user.tenant_id)
    role = await repo.update(rol_id, data)
    return _rol_to_response(role)


@router.delete("/roles/{rol_id}", response_model=RolResponse, dependencies=_admin_guard)
async def delete_role(
    rol_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = RolRepository(session=db, tenant_id=current_user.tenant_id)
    role = await repo.soft_delete(rol_id)
    return _rol_to_response(role)


# ── Permisos CRUD ──────────────────────────────────────────────────────


@router.get("/permisos", response_model=list[PermisoResponse], dependencies=_admin_guard)
async def list_permisos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = PermisoRepository(session=db, tenant_id=current_user.tenant_id)
    permisos = await repo.find_all(skip=skip, limit=limit)
    return [_permiso_to_response(p) for p in permisos]


@router.post("/permisos", response_model=PermisoResponse, status_code=201, dependencies=_admin_guard)
async def create_permiso(
    data: PermisoCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = PermisoRepository(session=db, tenant_id=current_user.tenant_id)
    permiso = await repo.create(data)
    return _permiso_to_response(permiso)


@router.get("/permisos/{permiso_id}", response_model=PermisoResponse, dependencies=_admin_guard)
async def get_permiso(
    permiso_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = PermisoRepository(session=db, tenant_id=current_user.tenant_id)
    permiso = await repo.find_by_id(permiso_id)
    if permiso is None:
        raise NotFoundException(resource="Permiso", id=permiso_id)
    return _permiso_to_response(permiso)


@router.put("/permisos/{permiso_id}", response_model=PermisoResponse, dependencies=_admin_guard)
async def update_permiso(
    permiso_id: UUID,
    data: PermisoUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = PermisoRepository(session=db, tenant_id=current_user.tenant_id)
    permiso = await repo.update(permiso_id, data)
    return _permiso_to_response(permiso)


@router.delete("/permisos/{permiso_id}", response_model=PermisoResponse, dependencies=_admin_guard)
async def delete_permiso(
    permiso_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = PermisoRepository(session=db, tenant_id=current_user.tenant_id)
    permiso = await repo.soft_delete(permiso_id)
    return _permiso_to_response(permiso)


# ── Rol-Permiso assignments ────────────────────────────────────────────


@router.post("/roles/{rol_id}/permisos", status_code=201, dependencies=_admin_guard)
async def assign_permiso_to_role(
    rol_id: UUID,
    data: RolPermisoCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = RolPermisoRepository(session=db, tenant_id=current_user.tenant_id)
    await repo.create(
        {
            "rol_id": rol_id,
            "permiso_id": data.permiso_id,
        }
    )
    return {"detail": "Permission assigned to role"}


@router.delete("/roles/{rol_id}/permisos/{permiso_id}", dependencies=_admin_guard)
async def remove_permiso_from_role(
    rol_id: UUID,
    permiso_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = RolPermisoRepository(session=db, tenant_id=current_user.tenant_id)
    existing = await repo.find_by(rol_id=rol_id, permiso_id=permiso_id)
    if not existing:
        raise NotFoundException(resource="RolPermiso")
    await repo.hard_delete(existing[0].id)
    return {"detail": "Permission removed from role"}


# ── Internal helpers ───────────────────────────────────────────────────


def _rol_to_response(role) -> RolResponse:
    return RolResponse(
        id=role.id,
        tenant_id=role.tenant_id,
        codigo=role.codigo,
        nombre=role.nombre,
        descripcion=role.descripcion,
        deleted_at=role.deleted_at is not None,
    )


def _permiso_to_response(permiso) -> PermisoResponse:
    return PermisoResponse(
        id=permiso.id,
        tenant_id=permiso.tenant_id,
        codigo=permiso.codigo,
        nombre=permiso.nombre,
        descripcion=permiso.descripcion,
        modulo=permiso.modulo,
        deleted_at=permiso.deleted_at is not None,
    )
