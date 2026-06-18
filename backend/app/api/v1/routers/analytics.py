"""Router for analytics API.

All endpoints are read-only (GET only). Non-GET methods return 405.
"""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.core.dependencies import get_db
from app.core.permissions import Perm
from app.schemas.analytics import (
    AtrasadosPorCohorteItem,
    DashboardResponse,
    DistribucionNotasItem,
    PrediccionAbandonoItem,
)
from app.schemas.auth import CurrentUser
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/admin/analytics", tags=["analytics"])


def _get_service(db: AsyncSession, current_user: CurrentUser) -> AnalyticsService:
    return AnalyticsService.create(db, current_user.tenant_id)


@router.api_route(
    "/dashboard",
    methods=["GET"],
    response_model=DashboardResponse,
    dependencies=[Depends(require_permission(Perm.AUDITORIA_VER))],
)
async def get_dashboard(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get consolidated analytics KPIs."""
    service = _get_service(db, current_user)
    return await service.get_dashboard()


@router.api_route(
    "/tendencias/atrasados-por-cohorte",
    methods=["GET"],
    response_model=list[AtrasadosPorCohorteItem],
    dependencies=[Depends(require_permission(Perm.AUDITORIA_VER))],
)
async def get_atrasados_por_cohorte(
    fecha_desde: date | None = Query(None),
    fecha_hasta: date | None = Query(None),
    carrera_id: UUID | None = Query(None),
    cohorte_id: UUID | None = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get atrasados grouped by cohorte."""
    service = _get_service(db, current_user)
    return await service.get_atrasados_por_cohorte(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        carrera_id=carrera_id,
        cohorte_id=cohorte_id,
    )


@router.api_route(
    "/tendencias/distribucion-notas",
    methods=["GET"],
    response_model=list[DistribucionNotasItem],
    dependencies=[Depends(require_permission(Perm.AUDITORIA_VER))],
)
async def get_distribucion_notas(
    dictado_id: UUID | None = Query(None),
    materia_id: UUID | None = Query(None),
    cohorte_id: UUID | None = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get grade distribution histogram."""
    service = _get_service(db, current_user)
    return await service.get_distribucion_notas(
        dictado_id=dictado_id,
        materia_id=materia_id,
        cohorte_id=cohorte_id,
    )


@router.api_route(
    "/prediccion/abandono",
    methods=["GET"],
    response_model=list[PrediccionAbandonoItem],
    dependencies=[Depends(require_permission(Perm.AUDITORIA_VER))],
)
async def get_prediccion_abandono(
    cohorte_id: UUID | None = Query(None),
    materia_id: UUID | None = Query(None),
    riesgo: str | None = Query(None),
    umbral: float = Query(60.0, ge=0.0, le=100.0),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get dropout risk prediction."""
    service = _get_service(db, current_user)
    return await service.get_prediccion_abandono(
        cohorte_id=cohorte_id,
        materia_id=materia_id,
        riesgo=riesgo,
        umbral=umbral,
    )


# ── 405 handler for non-GET methods ──────────────────────────────────


@router.api_route(
    "/{path:path}",
    methods=["POST", "PUT", "PATCH", "DELETE"],
)
async def method_not_allowed():
    """Reject non-GET methods on all analytics endpoints."""
    return JSONResponse(status_code=405, content={"detail": "Method Not Allowed"})
