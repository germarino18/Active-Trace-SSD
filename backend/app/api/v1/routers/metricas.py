from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.core.dependencies import get_db
from app.core.permissions import Perm
from app.models.asignacion import Asignacion
from app.models.carrera import Carrera
from app.models.materia import Materia
from app.models.usuario import Usuario
from app.schemas.auth import CurrentUser
from app.schemas.metricas import MetricasResponse

router = APIRouter(prefix="/api/admin", tags=["metricas"])

_metricas_guard = [Depends(require_permission(Perm.ESTRUCTURA_GESTIONAR))]


@router.get("/metricas", response_model=MetricasResponse, dependencies=_metricas_guard)
async def get_metricas(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tenant_id = current_user.tenant_id

    # Total alumnos: distinct usuarios con Asignacion.rol = 'ALUMNO'
    total_alumnos_q = (
        select(func.count(func.distinct(Asignacion.usuario_id)))
        .select_from(Asignacion)
        .where(Asignacion.rol == "ALUMNO", Asignacion.tenant_id == tenant_id, Asignacion.deleted_at.is_(None))
    )
    total_alumnos = (await db.execute(total_alumnos_q)).scalar() or 0

    # Alumnos activos: count of Usuario with estado='Activo' that have a 'ALUMNO' asignacion
    alumnos_activos_q = (
        select(func.count(func.distinct(Usuario.id)))
        .select_from(Usuario)
        .join(Asignacion, Usuario.id == Asignacion.usuario_id)
        .where(
            Asignacion.rol == "ALUMNO",
            Usuario.tenant_id == tenant_id,
            Usuario.estado == "Activo",
            Usuario.deleted_at.is_(None),
            Asignacion.deleted_at.is_(None),
        )
    )
    alumnos_activos = (await db.execute(alumnos_activos_q)).scalar() or 0

    # Total docentes: distinct usuarios con PROFESOR o TUTOR
    total_docentes_q = (
        select(func.count(func.distinct(Asignacion.usuario_id)))
        .select_from(Asignacion)
        .where(
            Asignacion.rol.in_(["PROFESOR", "TUTOR"]),
            Asignacion.tenant_id == tenant_id,
            Asignacion.deleted_at.is_(None),
        )
    )
    total_docentes = (await db.execute(total_docentes_q)).scalar() or 0

    # Materias activas
    materias_activas_q = (
        select(func.count(Materia.id))
        .where(Materia.tenant_id == tenant_id, Materia.estado == "Activa", Materia.deleted_at.is_(None))
    )
    total_materias_activas = (await db.execute(materias_activas_q)).scalar() or 0

    # Carreras activas
    carreras_activas_q = (
        select(func.count(Carrera.id))
        .where(Carrera.tenant_id == tenant_id, Carrera.estado == "Activa", Carrera.deleted_at.is_(None))
    )
    total_carreras_activas = (await db.execute(carreras_activas_q)).scalar() or 0

    return MetricasResponse(
        total_alumnos=total_alumnos,
        alumnos_activos=alumnos_activos,
        porcentaje_riesgo=0.0,
        promedio_progreso=0.0,
        total_docentes=total_docentes,
        total_materias_activas=total_materias_activas,
        total_carreras_activas=total_carreras_activas,
    )
