from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.core.dependencies import get_db
from app.core.exceptions import NotFoundException
from app.core.permissions import Perm
from app.models.asignacion import Asignacion
from app.repositories.asignacion_repository import AsignacionRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.carrera_repository import CarreraRepository
from app.repositories.cohorte_repository import CohorteRepository
from app.repositories.dictado_repository import DictadoRepository
from app.repositories.materia_repository import MateriaRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.asignacion import AsignacionCreate, AsignacionResponse, AsignacionUpdate
from app.schemas.auth import CurrentUser
from app.services.asignacion_service import AsignacionService, estado_vigencia_for

router = APIRouter(prefix="/api/asignaciones", tags=["asignaciones"])

# All asignaciones endpoints require equipos:asignar (D5/RBAC, Regla Dura #10).
_asignaciones_guard = [Depends(require_permission(Perm.EQUIPOS_ASIGNAR))]


@router.get("", response_model=list[AsignacionResponse], dependencies=_asignaciones_guard)
async def list_asignaciones(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = AsignacionRepository(session=db, tenant_id=current_user.tenant_id)
    asignaciones = await repo.find_all(skip=skip, limit=limit)
    return [_asignacion_to_response(a) for a in asignaciones]


@router.post("", response_model=AsignacionResponse, status_code=201, dependencies=_asignaciones_guard)
async def create_asignacion(
    data: AsignacionCreate,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = _asignacion_service(db, current_user.tenant_id)
    asignacion = await service.create(data, current_user=current_user, request=request)
    await db.commit()
    return _asignacion_to_response(asignacion)


@router.get("/{asignacion_id}", response_model=AsignacionResponse, dependencies=_asignaciones_guard)
async def get_asignacion(
    asignacion_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = AsignacionRepository(session=db, tenant_id=current_user.tenant_id)
    asignacion = await repo.find_by_id(asignacion_id)
    if asignacion is None:
        raise NotFoundException(resource="Asignacion", id=asignacion_id)
    return _asignacion_to_response(asignacion)


@router.patch("/{asignacion_id}", response_model=AsignacionResponse, dependencies=_asignaciones_guard)
async def update_asignacion(
    asignacion_id: UUID,
    data: AsignacionUpdate,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = AsignacionRepository(session=db, tenant_id=current_user.tenant_id)
    if await repo.find_by_id(asignacion_id) is None:
        raise NotFoundException(resource="Asignacion", id=asignacion_id)
    service = _asignacion_service(db, current_user.tenant_id)
    asignacion = await service.update(asignacion_id, data, current_user=current_user, request=request)
    await db.commit()
    return _asignacion_to_response(asignacion)


@router.delete("/{asignacion_id}", response_model=AsignacionResponse, dependencies=_asignaciones_guard)
async def delete_asignacion(
    asignacion_id: UUID,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = AsignacionRepository(session=db, tenant_id=current_user.tenant_id)
    if await repo.find_by_id(asignacion_id) is None:
        raise NotFoundException(resource="Asignacion", id=asignacion_id)
    service = _asignacion_service(db, current_user.tenant_id)
    asignacion = await service.soft_delete(asignacion_id, current_user=current_user, request=request)
    await db.commit()
    return _asignacion_to_response(asignacion)


# ── Service factory ──────────────────────────────────────────────────────


def _asignacion_service(db: AsyncSession, tenant_id: UUID) -> AsignacionService:
    return AsignacionService(
        asignacion_repo=AsignacionRepository(session=db, tenant_id=tenant_id),
        usuario_repo=UsuarioRepository(session=db, tenant_id=tenant_id),
        dictado_repo=DictadoRepository(session=db, tenant_id=tenant_id),
        materia_repo=MateriaRepository(session=db, tenant_id=tenant_id),
        carrera_repo=CarreraRepository(session=db, tenant_id=tenant_id),
        cohorte_repo=CohorteRepository(session=db, tenant_id=tenant_id),
        audit_repo=AuditLogRepository(session=db, tenant_id=tenant_id),
    )


# ── Response mapper ───────────────────────────────────────────────────────


def _asignacion_to_response(asignacion: Asignacion) -> AsignacionResponse:
    return AsignacionResponse(
        id=asignacion.id,
        tenant_id=asignacion.tenant_id,
        usuario_id=asignacion.usuario_id,
        rol=asignacion.rol,
        dictado_id=asignacion.dictado_id,
        materia_id=asignacion.materia_id,
        carrera_id=asignacion.carrera_id,
        cohorte_id=asignacion.cohorte_id,
        comisiones=list(asignacion.comisiones or []),
        responsable_id=asignacion.responsable_id,
        desde=asignacion.desde,
        hasta=asignacion.hasta,
        estado_vigencia=estado_vigencia_for(asignacion),
        deleted_at=asignacion.deleted_at is not None,
    )
