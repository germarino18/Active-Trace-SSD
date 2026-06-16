from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.core.dependencies import get_db
from app.core.permissions import Perm
from app.schemas.auth import CurrentUser
from app.schemas.coloquios import (
    AgendaReservaRead,
    AlumnoConvocadoCreate,
    EvaluacionCreate,
    EvaluacionRead,
    EvaluacionUpdate,
    MetricasColoquiosRead,
    RegistroAcademicoRead,
    ReservaEvaluacionCreate,
    ReservaEvaluacionRead,
    ResultadoEvaluacionCreate,
    ResultadoEvaluacionRead,
)
from app.services.coloquios import ColoquioService
from app.services.coloquios.reserva_service import ReservaService
from app.services.coloquios.resultado_service import ResultadoService

_gestionar_guard = [Depends(require_permission(Perm.COLOQUIOS_GESTIONAR))]
_reservar_guard = [Depends(require_permission(Perm.COLOQUIOS_RESERVAR))]
_ver_guard = [Depends(require_permission(Perm.COLOQUIOS_VER))]

router = APIRouter(
    prefix="/api/v1/coloquios",
    tags=["Coloquios"],
    dependencies=[Depends(get_current_user)],
)


# ── Gestión (coloquios:gestionar) ────────────────────────────────────────

@router.post("", response_model=EvaluacionRead, status_code=201, dependencies=_gestionar_guard)
async def crear_evaluacion(
    data: EvaluacionCreate,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Create a new coloquio convocatoria."""
    service = ColoquioService.create(db, current_user.tenant_id)
    return await service.crear_evaluacion(
        data, current_user=current_user, request=request
    )


@router.patch("/{evaluacion_id}", response_model=EvaluacionRead, dependencies=_gestionar_guard)
async def actualizar_evaluacion(
    evaluacion_id: UUID,
    data: EvaluacionUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Update a convocatoria (metadata only, if Activa)."""
    service = ColoquioService.create(db, current_user.tenant_id)
    return await service.actualizar_evaluacion(
        evaluacion_id, data, current_user=current_user, request=request
    )


@router.post("/{evaluacion_id}/cerrar", response_model=EvaluacionRead, dependencies=_gestionar_guard)
async def cerrar_evaluacion(
    evaluacion_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Close a convocatoria (estado -> Cerrada)."""
    service = ColoquioService.create(db, current_user.tenant_id)
    return await service.cerrar_evaluacion(
        evaluacion_id, current_user=current_user, request=request
    )


@router.post("/{evaluacion_id}/importar-alumnos", dependencies=_gestionar_guard)
async def importar_alumnos(
    evaluacion_id: UUID,
    data: AlumnoConvocadoCreate,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Import alumnos to a convocatoria (idempotent)."""
    service = ColoquioService.create(db, current_user.tenant_id)
    count = await service.importar_alumnos(
        evaluacion_id,
        data.alumno_ids,
        current_user=current_user,
        request=request,
    )
    return {"importados": count}


# ── Reserva (coloquios:reservar) ─────────────────────────────────────────

@router.post("/{evaluacion_id}/reservar", response_model=ReservaEvaluacionRead, dependencies=_reservar_guard)
async def reservar_turno(
    evaluacion_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Reserve a turno in a convocatoria (ALUMNO)."""
    service = ReservaService.create(db, current_user.tenant_id)
    return await service.reservar(
        evaluacion_id, current_user=current_user, request=request
    )


@router.post(
    "/reservas/{reserva_id}/cancelar",
    response_model=ReservaEvaluacionRead,
    dependencies=_reservar_guard,
)
async def cancelar_reserva(
    reserva_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Cancel a reservation (by owner or coloquios:gestionar)."""
    service = ReservaService.create(db, current_user.tenant_id)
    return await service.cancelar_reserva(
        reserva_id, current_user=current_user, request=request
    )


# ── Resultados (coloquios:gestionar) ─────────────────────────────────────

@router.post(
    "/{evaluacion_id}/resultados",
    response_model=ResultadoEvaluacionRead,
    status_code=201,
    dependencies=_gestionar_guard,
)
async def registrar_resultado(
    evaluacion_id: UUID,
    data: ResultadoEvaluacionCreate,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Register a coloquio result (immutable)."""
    service = ResultadoService.create(db, current_user.tenant_id)
    return await service.registrar_resultado(
        data, current_user=current_user, request=request
    )


# ── Consulta (coloquios:ver) ─────────────────────────────────────────────

@router.get("", response_model=list[EvaluacionRead], dependencies=_ver_guard)
async def listar_evaluaciones(
    dictado_id: UUID | None = Query(None),
    estado: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List convocatorias with optional filters."""
    service = ColoquioService.create(db, current_user.tenant_id)
    return await service.listar_evaluaciones(
        dictado_id=dictado_id,
        estado=estado,
        skip=skip,
        limit=limit,
    )


@router.get("/metricas", response_model=MetricasColoquiosRead, dependencies=_ver_guard)
async def metricas_coloquios(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get panel metrics for coloquios."""
    service = ColoquioService.create(db, current_user.tenant_id)
    return await service.metricas()


@router.get("/reservas", response_model=list[AgendaReservaRead], dependencies=_ver_guard)
async def listar_agenda(
    evaluacion_id: UUID | None = Query(None),
    alumno_id: UUID | None = Query(None),
    dictado_id: UUID | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List active reservations (agenda view)."""
    service = ReservaService.create(db, current_user.tenant_id)
    return await service.listar_agenda(
        evaluacion_id=evaluacion_id,
        alumno_id=alumno_id,
        dictado_id=dictado_id,
        skip=skip,
        limit=limit,
    )


@router.get("/resultados", response_model=list[RegistroAcademicoRead], dependencies=_ver_guard)
async def registro_academico(
    dictado_id: UUID | None = Query(None),
    evaluacion_id: UUID | None = Query(None),
    alumno_id: UUID | None = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get consolidated academic record of coloquio results."""
    service = ColoquioService.create(db, current_user.tenant_id)
    return await service.registro_academico(
        dictado_id=dictado_id,
        evaluacion_id=evaluacion_id,
        alumno_id=alumno_id,
    )


@router.get("/{evaluacion_id}", response_model=EvaluacionRead, dependencies=_ver_guard)
async def obtener_evaluacion(
    evaluacion_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get convocatoria details."""
    service = ColoquioService.create(db, current_user.tenant_id)
    return await service.obtener_evaluacion(evaluacion_id)
