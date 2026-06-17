"""Router for auditoria (audit panel and metrics) API.

All endpoints are read-only (GET only). Non-GET methods return 405.
"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.core.dependencies import get_db
from app.core.permissions import Perm
from app.schemas.auditoria import (
    AccionesPorDiaItem,
    ComunicacionesPorDocenteItem,
    InteraccionesPorDocenteMateriaItem,
    LogAuditoriaPaginado,
    UltimasAccionesResponse,
)
from app.schemas.auth import CurrentUser
from app.services.auditoria_service import AuditoriaService

router = APIRouter(prefix="/api/v1/auditoria", tags=["auditoria"])


def _get_service(db: AsyncSession, current_user: CurrentUser) -> AuditoriaService:
    return AuditoriaService.create(db, current_user.tenant_id)


@router.api_route(
    "/acciones-por-dia",
    methods=["GET"],
    response_model=list[AccionesPorDiaItem],
    dependencies=[Depends(require_permission(Perm.AUDITORIA_VER))],
)
async def acciones_por_dia(
    fecha_desde: datetime | None = Query(None),
    fecha_hasta: datetime | None = Query(None),
    usuario_id: UUID | None = Query(None),
    materia_id: UUID | None = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get daily action counts (time series)."""
    service = _get_service(db, current_user)
    return await service.get_acciones_por_dia(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        usuario_id=usuario_id,
        materia_id=materia_id,
        user_id=current_user.user_id,
        roles=current_user.roles,
    )


@router.api_route(
    "/comunicaciones-por-docente",
    methods=["GET"],
    response_model=list[ComunicacionesPorDocenteItem],
    dependencies=[Depends(require_permission(Perm.AUDITORIA_VER))],
)
async def comunicaciones_por_docente(
    fecha_desde: datetime | None = Query(None),
    fecha_hasta: datetime | None = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get communication state distribution grouped by docente and materia."""
    service = _get_service(db, current_user)
    return await service.get_comunicaciones_por_docente(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        user_id=current_user.user_id,
        roles=current_user.roles,
    )


@router.api_route(
    "/interacciones-por-docente-materia",
    methods=["GET"],
    response_model=list[InteraccionesPorDocenteMateriaItem],
    dependencies=[Depends(require_permission(Perm.AUDITORIA_VER))],
)
async def interacciones_por_docente_materia(
    fecha_desde: datetime | None = Query(None),
    fecha_hasta: datetime | None = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get usage metrics by docente and materia, broken down by action type."""
    service = _get_service(db, current_user)
    return await service.get_interacciones_por_docente_materia(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        user_id=current_user.user_id,
        roles=current_user.roles,
    )


@router.api_route(
    "/ultimas-acciones",
    methods=["GET"],
    response_model=UltimasAccionesResponse,
    dependencies=[Depends(require_permission(Perm.AUDITORIA_VER))],
)
async def ultimas_acciones(
    limit: int = Query(200, ge=1, le=1000),
    fecha_desde: datetime | None = Query(None),
    fecha_hasta: datetime | None = Query(None),
    materia_id: UUID | None = Query(None),
    usuario_id: UUID | None = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the most recent audit log entries (configurable limit, max 1000)."""
    service = _get_service(db, current_user)
    return await service.get_ultimas_acciones(
        limit=limit,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        materia_id=materia_id,
        usuario_id=usuario_id,
        user_id=current_user.user_id,
        roles=current_user.roles,
    )


@router.api_route(
    "/log",
    methods=["GET"],
    response_model=LogAuditoriaPaginado,
    dependencies=[Depends(require_permission(Perm.AUDITORIA_VER))],
)
async def log_auditoria(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    fecha_desde: datetime | None = Query(None),
    fecha_hasta: datetime | None = Query(None),
    materia_id: UUID | None = Query(None),
    usuario_id: UUID | None = Query(None),
    accion: str | None = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the full audit log with combined filters and pagination."""
    service = _get_service(db, current_user)
    return await service.get_log_auditoria(
        offset=offset,
        limit=limit,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        materia_id=materia_id,
        usuario_id=usuario_id,
        accion=accion,
        user_id=current_user.user_id,
        roles=current_user.roles,
    )


# ── 405 handler for non-GET methods ──────────────────────────────────


@router.api_route(
    "/{path:path}",
    methods=["POST", "PUT", "PATCH", "DELETE"],
)
async def method_not_allowed():
    """Reject non-GET methods on all auditoria endpoints."""
    return JSONResponse(status_code=405, content={"detail": "Method Not Allowed"})
