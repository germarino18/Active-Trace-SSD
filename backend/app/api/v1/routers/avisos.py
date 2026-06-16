"""Router for avisos (announcements with acknowledgment)."""

from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.core.dependencies import get_db
from app.core.permissions import Perm
from app.schemas.auth import CurrentUser
from app.schemas.avisos import (
    AcknowledgmentStats,
    AvisoCreate,
    AvisoListParams,
    AvisoRead,
    AvisoUpdate,
    AvisoVisibleRead,
    ConfirmResponse,
)
from app.services.avisos_service import AvisoService

router = APIRouter(prefix="/api/v1/avisos", tags=["avisos"])


# ── Static paths (BEFORE parameterized paths) ─────────────────────


@router.get("/visible", response_model=list[AvisoVisibleRead])
async def avisos_visibles(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get avisos visible to the current user."""
    service = AvisoService.create(db, current_user.tenant_id)
    return await service.get_visible(current_user)


@router.get("/pendientes", response_model=list[AvisoVisibleRead])
async def avisos_pendientes(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get pending acknowledgments for the current user."""
    service = AvisoService.create(db, current_user.tenant_id)
    return await service.get_pendientes(current_user)


# ── CRUD ───────────────────────────────────────────────────────────


@router.post("", response_model=AvisoRead, status_code=201, dependencies=[Depends(require_permission(Perm.AVISOS_PUBLICAR))])
async def create_aviso(
    req: AvisoCreate,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Create a new aviso."""
    service = AvisoService.create(db, current_user.tenant_id)
    return await service.create_aviso(data=req, current_user=current_user, request=request)


@router.get("", response_model=list[AvisoRead], dependencies=[Depends(require_permission(Perm.AVISOS_PUBLICAR))])
async def list_avisos(
    params: AvisoListParams = Depends(),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all managed avisos (with pagination)."""
    service = AvisoService.create(db, current_user.tenant_id)
    return await service.get_all_managed(skip=params.skip, limit=params.limit)


@router.get("/{aviso_id}", response_model=AvisoRead, dependencies=[Depends(require_permission(Perm.AVISOS_PUBLICAR))])
async def get_aviso(
    aviso_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single aviso."""
    service = AvisoService.create(db, current_user.tenant_id)
    return await service.get_by_id(aviso_id)


@router.patch("/{aviso_id}", response_model=AvisoRead, dependencies=[Depends(require_permission(Perm.AVISOS_PUBLICAR))])
async def update_aviso(
    aviso_id: UUID,
    req: AvisoUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing aviso."""
    service = AvisoService.create(db, current_user.tenant_id)
    return await service.update(aviso_id, data=req, current_user=current_user, request=request)


@router.delete("/{aviso_id}", status_code=204, dependencies=[Depends(require_permission(Perm.AVISOS_PUBLICAR))])
async def delete_aviso(
    aviso_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete an aviso."""
    service = AvisoService.create(db, current_user.tenant_id)
    await service.delete(aviso_id, current_user=current_user, request=request)


# ── Actions ────────────────────────────────────────────────────────


@router.post("/{aviso_id}/confirmar", response_model=ConfirmResponse, dependencies=[Depends(require_permission(Perm.AVISOS_CONFIRMAR))])
async def confirmar_aviso(
    aviso_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Confirm (acknowledge) an aviso."""
    service = AvisoService.create(db, current_user.tenant_id)
    return await service.confirmar(aviso_id, current_user=current_user, request=request)


@router.get("/{aviso_id}/stats", response_model=AcknowledgmentStats, dependencies=[Depends(require_permission(Perm.AVISOS_PUBLICAR))])
async def aviso_stats(
    aviso_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get acknowledgment statistics for an aviso."""
    service = AvisoService.create(db, current_user.tenant_id)
    return await service.get_stats(aviso_id, current_user=current_user)
