"""Router for the alumno (student) module — dashboard + student-facing endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.core.dependencies import get_db
from app.core.permissions import Perm
from app.schemas.alumno import (
    AlumnoDashboardResponse,
    ComunicacionDetalleRead,
    ComunicacionRecibidaRead,
    EstadoAcademicoMateria,
    ProgramaMateriaRead,
)
from app.schemas.auth import CurrentUser
from app.services.alumno_service import AlumnoService

router = APIRouter(prefix="/api/v1/alumno", tags=["alumno"])


@router.get(
    "/dashboard",
    response_model=AlumnoDashboardResponse,
    dependencies=[Depends(require_permission(Perm.ESTADO_ACADEMICO_VER))],
)
async def get_alumno_dashboard(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Aggregated dashboard for the authenticated student."""
    service = AlumnoService(db=db, tenant_id=current_user.tenant_id, current_user=current_user)
    return await service.get_dashboard()


@router.get(
    "/materias",
    response_model=list[EstadoAcademicoMateria],
    dependencies=[Depends(require_permission(Perm.ESTADO_ACADEMICO_VER))],
)
async def list_materias(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List the student's subjects with academic status."""
    service = AlumnoService(db=db, tenant_id=current_user.tenant_id, current_user=current_user)
    return await service.get_materias()


@router.get(
    "/materias/{materia_id}",
    response_model=EstadoAcademicoMateria,
    dependencies=[Depends(require_permission(Perm.ESTADO_ACADEMICO_VER))],
)
async def get_materia_detalle(
    materia_id: UUID = Path(...),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed academic status for a specific subject."""
    service = AlumnoService(db=db, tenant_id=current_user.tenant_id, current_user=current_user)
    return await service.get_materia_detalle(materia_id)


@router.get(
    "/programas",
    response_model=list[ProgramaMateriaRead],
    dependencies=[Depends(require_permission(Perm.ESTADO_ACADEMICO_VER))],
)
async def list_programas(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List programs for the student's subjects."""
    service = AlumnoService(db=db, tenant_id=current_user.tenant_id, current_user=current_user)
    return await service.get_programas()


@router.get(
    "/fechas",
    response_model=list,
    dependencies=[Depends(require_permission(Perm.ESTADO_ACADEMICO_VER))],
)
async def list_fechas(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List academic dates for the student's subjects."""
    service = AlumnoService(db=db, tenant_id=current_user.tenant_id, current_user=current_user)
    return await service.get_fechas()


@router.get(
    "/comunicaciones",
    response_model=list[ComunicacionRecibidaRead],
    dependencies=[Depends(require_permission(Perm.ESTADO_ACADEMICO_VER))],
)
async def list_comunicaciones(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List communications received by the student."""
    service = AlumnoService(db=db, tenant_id=current_user.tenant_id, current_user=current_user)
    return await service.get_comunicaciones()


@router.get(
    "/comunicaciones/{comunicacion_id}",
    response_model=ComunicacionDetalleRead,
    dependencies=[Depends(require_permission(Perm.ESTADO_ACADEMICO_VER))],
)
async def get_comunicacion_detalle(
    comunicacion_id: UUID = Path(...),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get full detail of a received communication."""
    service = AlumnoService(db=db, tenant_id=current_user.tenant_id, current_user=current_user)
    return await service.get_comunicacion_detalle(comunicacion_id)
