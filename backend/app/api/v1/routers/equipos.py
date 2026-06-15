import csv
import io
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.core.dependencies import get_db
from app.core.permissions import Perm
from app.models.asignacion import Asignacion
from app.repositories.asignacion_repository import AsignacionRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.carrera_repository import CarreraRepository
from app.repositories.cohorte_repository import CohorteRepository
from app.repositories.materia_repository import MateriaRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.asignacion import EstadoVigencia, RolAsignacion
from app.schemas.auth import CurrentUser
from app.schemas.equipo import (
    AsignacionMasivaCreate,
    AsignacionMasivaResultado,
    ClonarEquipoCreate,
    DocenteResponse,
    EquipoAsignacionResponse,
    EquipoFiltros,
    MisEquiposFiltros,
    VigenciaEquipoUpdate,
)
from app.services.asignacion_service import estado_vigencia_for
from app.services.equipo_service import EquipoService

router = APIRouter(prefix="/api/equipos", tags=["equipos"])

# Coordination endpoints (F4.3-F4.7) require equipos:asignar, fail-closed
# (D3 [SEC], regla dura #10). "mis-equipos" (F4.2) is session-only — NO
# guard here (D3).
_equipos_guard = [Depends(require_permission(Perm.EQUIPOS_ASIGNAR))]


@router.get("/mis-equipos", response_model=list[EquipoAsignacionResponse])
async def mis_equipos(
    estado: EstadoVigencia | None = Query(None),
    materia_id: UUID | None = Query(None),
    rol: RolAsignacion | None = Query(None),
    carrera_id: UUID | None = Query(None),
    cohorte_id: UUID | None = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Asignaciones VIGENTES del docente autenticado (F4.2, D3 [SEC]).

    `usuario_id`/`tenant_id` salen EXCLUSIVAMENTE de `current_user`
    (regla dura #8) -- nunca de un parámetro. Autorizado por sesión
    válida; no exige `equipos:asignar`.
    """
    service = _equipo_service(db, current_user.tenant_id)
    filtros = MisEquiposFiltros(
        estado=estado, materia_id=materia_id, rol=rol, carrera_id=carrera_id, cohorte_id=cohorte_id
    )
    items = await service.mis_equipos(current_user, filtros=filtros)
    return [
        EquipoAsignacionResponse(
            id=item.id,
            usuario_id=item.usuario_id,
            rol=item.rol,
            dictado_id=item.dictado_id,
            materia_id=item.materia_id,
            carrera_id=item.carrera_id,
            cohorte_id=item.cohorte_id,
            comisiones=list(item.comisiones or []),
            responsable_id=item.responsable_id,
            desde=item.desde,
            hasta=item.hasta,
            estado_vigencia=item.estado_vigencia,
        )
        for item in items
    ]


@router.get("/docentes", response_model=list[DocenteResponse], dependencies=_equipos_guard)
async def buscar_docentes(
    q: str = Query(..., min_length=1),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Autocompletado de docentes para asignación masiva (F4.4, RN-30)."""
    service = _equipo_service(db, current_user.tenant_id)
    return await service.buscar_docentes(current_user.tenant_id, q)


@router.get("", response_model=list[EquipoAsignacionResponse], dependencies=_equipos_guard)
async def listar_equipos(
    materia_id: UUID | None = Query(None),
    carrera_id: UUID | None = Query(None),
    cohorte_id: UUID | None = Query(None),
    usuario_id: UUID | None = Query(None),
    rol: RolAsignacion | None = Query(None),
    responsable_id: UUID | None = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Listado filtrable de asignaciones vivas del tenant (F4.3)."""
    service = _equipo_service(db, current_user.tenant_id)
    filtros = EquipoFiltros(
        materia_id=materia_id,
        carrera_id=carrera_id,
        cohorte_id=cohorte_id,
        usuario_id=usuario_id,
        rol=rol,
        responsable_id=responsable_id,
    )
    rows = await service.listar_equipos(current_user.tenant_id, filtros=filtros)
    return [_asignacion_to_equipo_response(row) for row in rows]


@router.get("/export", dependencies=_equipos_guard)
async def exportar_equipo(
    materia_id: UUID = Query(...),
    carrera_id: UUID = Query(...),
    cohorte_id: UUID = Query(...),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export CSV descargable del equipo (F4.7, D8). Sólo lectura: no audita."""
    service = _equipo_service(db, current_user.tenant_id)
    items = await service.exportar_equipo(
        {"materia_id": materia_id, "carrera_id": carrera_id, "cohorte_id": cohorte_id},
        current_user=current_user,
    )

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["docente", "rol", "materia_id", "carrera_id", "cohorte_id", "desde", "hasta", "estado_vigencia"])
    for item in items:
        writer.writerow([
            item.docente,
            item.rol.value if hasattr(item.rol, "value") else item.rol,
            str(item.materia_id) if item.materia_id else "",
            str(item.carrera_id) if item.carrera_id else "",
            str(item.cohorte_id) if item.cohorte_id else "",
            str(item.desde),
            str(item.hasta) if item.hasta else "",
            item.estado_vigencia.value if hasattr(item.estado_vigencia, "value") else item.estado_vigencia,
        ])
    buffer.seek(0)

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=equipo.csv"},
    )


@router.post("/asignacion-masiva", response_model=AsignacionMasivaResultado, dependencies=_equipos_guard)
async def asignacion_masiva(
    data: AsignacionMasivaCreate,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Asignación masiva de N docentes (F4.4, RN-30, D5/D6). Transaccional:
    un único `await db.commit()` al final."""
    service = _equipo_service(db, current_user.tenant_id)
    resultado = await service.asignacion_masiva(data, current_user=current_user, request=request)
    await db.commit()
    return resultado


@router.post("/clonar", response_model=AsignacionMasivaResultado, dependencies=_equipos_guard)
async def clonar_equipo(
    data: ClonarEquipoCreate,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Clonado de equipo entre períodos (F4.5, RN-12, D5/D6). Transaccional:
    un único `await db.commit()` al final."""
    service = _equipo_service(db, current_user.tenant_id)
    resultado = await service.clonar_equipo(data, current_user=current_user, request=request)
    await db.commit()
    return resultado


@router.patch("/vigencia", dependencies=_equipos_guard)
async def modificar_vigencia(
    data: VigenciaEquipoUpdate,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Modificación de vigencia del equipo en bloque (F4.6, D6).
    Transaccional: un único `await db.commit()` al final."""
    service = _equipo_service(db, current_user.tenant_id)
    filas_afectadas = await service.modificar_vigencia(data, current_user=current_user, request=request)
    await db.commit()
    return {"filas_afectadas": filas_afectadas}


# ── Service factory ──────────────────────────────────────────────────────


def _equipo_service(db: AsyncSession, tenant_id: UUID) -> EquipoService:
    return EquipoService(
        asignacion_repo=AsignacionRepository(session=db, tenant_id=tenant_id),
        usuario_repo=UsuarioRepository(session=db, tenant_id=tenant_id),
        materia_repo=MateriaRepository(session=db, tenant_id=tenant_id),
        carrera_repo=CarreraRepository(session=db, tenant_id=tenant_id),
        cohorte_repo=CohorteRepository(session=db, tenant_id=tenant_id),
        audit_repo=AuditLogRepository(session=db, tenant_id=tenant_id),
    )


# ── Response mapper ───────────────────────────────────────────────────────


def _asignacion_to_equipo_response(asignacion: Asignacion) -> EquipoAsignacionResponse:
    return EquipoAsignacionResponse(
        id=asignacion.id,
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
    )
