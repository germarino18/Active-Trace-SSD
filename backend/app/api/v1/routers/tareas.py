"""Router for tareas (internal task management with state machine)."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.core.dependencies import get_db
from app.core.exceptions import ForbiddenException
from app.core.permissions import Perm
from app.schemas.auth import CurrentUser
from app.schemas.tareas import (
    ComentarioCreate,
    ComentarioRead,
    TareaCreate,
    TareaFilterParams,
    TareaRead,
    TareaUpdateEstado,
)
from app.services.tareas_service import TareasService

router = APIRouter(prefix="/api/v1/tareas", tags=["tareas"])

_COORD_ADMIN = {"COORDINADOR", "ADMIN"}


# ── Static paths (BEFORE parameterized paths) ─────────────────────


@router.get("/mias", response_model=list[TareaRead], dependencies=[Depends(require_permission(Perm.TAREAS_GESTIONAR))])
async def mis_tareas(
    estado: str | None = Query(None),
    materia_id: UUID | None = Query(None),
    texto: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get tasks assigned to the current user."""
    service = TareasService.create(db, current_user.tenant_id)
    return await service.get_mis_tareas(
        current_user, estado=estado, materia_id=materia_id,
        texto=texto, skip=skip, limit=limit,
    )


# ── CRUD ───────────────────────────────────────────────────────────


@router.post("", response_model=TareaRead, status_code=201, dependencies=[Depends(require_permission(Perm.TAREAS_GESTIONAR))])
async def create_tarea(
    req: TareaCreate,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Create a new task (COORDINADOR/ADMIN only)."""
    if not any(r in _COORD_ADMIN for r in current_user.roles):
        raise ForbiddenException(action="Crear tarea")
    service = TareasService.create(db, current_user.tenant_id)
    return await service.create_tarea(data=req, current_user=current_user, request=request)


@router.get("", response_model=list[TareaRead], dependencies=[Depends(require_permission(Perm.TAREAS_GESTIONAR))])
async def list_tareas(
    estado: str | None = Query(None),
    materia_id: UUID | None = Query(None),
    asignado_a_id: UUID | None = Query(None),
    texto: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all tasks for admin (COORDINADOR/ADMIN only)."""
    if not any(r in _COORD_ADMIN for r in current_user.roles):
        raise ForbiddenException(action="Listar tareas")
    service = TareasService.create(db, current_user.tenant_id)
    return await service.get_all_managed(
        current_user, estado=estado, materia_id=materia_id,
        asignado_a_id=asignado_a_id, texto=texto,
        skip=skip, limit=limit,
    )


@router.get("/{tarea_id}", response_model=TareaRead, dependencies=[Depends(require_permission(Perm.TAREAS_GESTIONAR))])
async def get_tarea(
    tarea_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single task with comments."""
    service = TareasService.create(db, current_user.tenant_id)
    return await service.get_tarea(tarea_id, current_user)


@router.patch("/{tarea_id}/estado", response_model=TareaRead, dependencies=[Depends(require_permission(Perm.TAREAS_GESTIONAR))])
async def cambiar_estado(
    tarea_id: UUID,
    req: TareaUpdateEstado,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Change task state with optional auto-comment."""
    service = TareasService.create(db, current_user.tenant_id)
    return await service.cambiar_estado(
        tarea_id, data=req, current_user=current_user, request=request,
    )


@router.delete("/{tarea_id}", status_code=204, dependencies=[Depends(require_permission(Perm.TAREAS_GESTIONAR))])
async def delete_tarea(
    tarea_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a task (COORDINADOR/ADMIN only)."""
    if not any(r in _COORD_ADMIN for r in current_user.roles):
        raise ForbiddenException(action="Eliminar tarea")
    service = TareasService.create(db, current_user.tenant_id)
    await service.delete_tarea(tarea_id, current_user=current_user, request=request)


@router.post("/{tarea_id}/comentarios", response_model=ComentarioRead, status_code=201, dependencies=[Depends(require_permission(Perm.TAREAS_GESTIONAR))])
async def add_comentario(
    tarea_id: UUID,
    req: ComentarioCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a comment to a task."""
    service = TareasService.create(db, current_user.tenant_id)
    return await service.agregar_comentario(tarea_id, req.texto, current_user)
