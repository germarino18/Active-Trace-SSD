from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.core.dependencies import get_db
from app.core.permissions import Perm
from app.schemas.analisis import (
    AlumnoAtrasado,
    MonitorPaginado,
    NotaFinalAlumno,
    RankingItem,
    ReporteMateria,
    TPSinCorregir,
)
from app.schemas.auth import CurrentUser
from app.services.analisis.analisis_service import AnalisisService

router = APIRouter(prefix="/api/admin/analisis", tags=["analisis"])


@router.get(
    "/atrasados",
    response_model=list[AlumnoAtrasado],
    dependencies=[Depends(require_permission(Perm.ATRASADOS_VER))],
)
async def get_alumnos_atrasados(
    dictado_id: UUID = Query(...),
    current_user: CurrentUser = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db),
):
    service = AnalisisService(db_session, current_user.tenant_id, current_user.user_id)
    return await service.get_alumnos_atrasados(dictado_id)


@router.get(
    "/ranking",
    response_model=list[RankingItem],
    dependencies=[Depends(require_permission(Perm.ATRASADOS_VER))],
)
async def get_ranking_aprobadas(
    dictado_id: UUID = Query(...),
    current_user: CurrentUser = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db),
):
    service = AnalisisService(db_session, current_user.tenant_id, current_user.user_id)
    return await service.get_ranking_aprobadas(dictado_id)


@router.get(
    "/reportes/materia/{dictado_id}",
    response_model=ReporteMateria,
    dependencies=[Depends(require_permission(Perm.ATRASADOS_VER))],
)
async def get_reporte_materia(
    dictado_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db),
):
    service = AnalisisService(db_session, current_user.tenant_id, current_user.user_id)
    return await service.get_reporte_materia(dictado_id)


@router.get(
    "/notas-finales",
    response_model=list[NotaFinalAlumno],
    dependencies=[Depends(require_permission(Perm.ATRASADOS_VER))],
)
async def get_notas_finales(
    dictado_id: UUID = Query(...),
    current_user: CurrentUser = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db),
):
    service = AnalisisService(db_session, current_user.tenant_id, current_user.user_id)
    return await service.get_notas_finales(dictado_id)


@router.get(
    "/tps-sin-corregir/export",
    response_model=list[TPSinCorregir],
    dependencies=[Depends(require_permission(Perm.ATRASADOS_VER))],
)
async def get_tps_sin_corregir(
    dictado_id: UUID = Query(...),
    current_user: CurrentUser = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db),
):
    service = AnalisisService(db_session, current_user.tenant_id, current_user.user_id)
    try:
        return await service.get_tps_sin_corregir(dictado_id, finalizaciones=[])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/monitor/general",
    response_model=MonitorPaginado,
    dependencies=[Depends(require_permission(Perm.ATRASADOS_VER))],
)
async def get_monitor_general(
    dictado_id: UUID | None = Query(default=None),
    comision: str | None = Query(default=None),
    q: str | None = Query(default=None),
    estado: str | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    current_user: CurrentUser = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db),
):
    service = AnalisisService(db_session, current_user.tenant_id, current_user.user_id)
    return await service.get_monitor_general(
        dictado_id=dictado_id,
        comision=comision,
        q=q,
        estado=estado,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/monitor/seguimiento",
    response_model=MonitorPaginado,
    dependencies=[Depends(require_permission(Perm.ATRASADOS_VER))],
)
async def get_monitor_seguimiento(
    dictado_id: UUID | None = Query(default=None),
    comision: str | None = Query(default=None),
    q: str | None = Query(default=None),
    minimo_cumplidas: int | None = Query(default=None, ge=1),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    desde: str | None = Query(default=None),
    hasta: str | None = Query(default=None),
    current_user: CurrentUser = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db),
):
    service = AnalisisService(db_session, current_user.tenant_id, current_user.user_id)
    return await service.get_monitor_general(
        dictado_id=dictado_id,
        comision=comision,
        q=q,
        offset=offset,
        limit=limit,
    )
