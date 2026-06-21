"""Router para actividades evaluables (C-25).

Endpoints:
  GET    /api/v1/actividades/dictados/{dictado_id}                  — listar actividades
  POST   /api/v1/actividades/dictados/{dictado_id}                  — crear actividad
  PATCH  /api/v1/actividades/{actividad_id}                         — editar actividad
  DELETE /api/v1/actividades/{actividad_id}                         — soft-delete actividad
  GET    /api/v1/actividades/{actividad_id}/plantilla-csv           — descargar plantilla CSV (pre-filled)
  POST   /api/v1/actividades/{actividad_id}/calificaciones-csv      — subir notas CSV
  POST   /api/v1/actividades/{actividad_id}/calificaciones          — registrar calificacion individual (modal)
"""

import csv
import io
from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.core.dependencies import get_db
from app.core.permissions import Perm
from app.schemas.actividades import ActividadCreate, ActividadResponse, ActividadUpdate
from app.schemas.auth import CurrentUser
from app.services.actividad_service import ActividadService

router = APIRouter(prefix="/api/v1/actividades", tags=["actividades"])


@router.get(
    "/dictados/{dictado_id}",
    response_model=list[ActividadResponse],
    dependencies=[Depends(require_permission(Perm.ACTIVIDADES_GESTIONAR))],
)
async def listar_actividades(
    dictado_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ActividadResponse]:
    """Lista las actividades vivas de un dictado."""
    service = ActividadService.create(db, current_user.tenant_id)
    actividades = await service.listar(dictado_id)
    return [ActividadResponse.model_validate(a) for a in actividades]


@router.post(
    "/dictados/{dictado_id}",
    response_model=ActividadResponse,
    status_code=201,
    dependencies=[Depends(require_permission(Perm.ACTIVIDADES_GESTIONAR))],
)
async def crear_actividad(
    dictado_id: UUID,
    data: ActividadCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ActividadResponse:
    """Crea una actividad en el dictado."""
    service = ActividadService.create(db, current_user.tenant_id)
    actividad = await service.crear(dictado_id, data)
    await db.commit()
    await db.refresh(actividad)
    return ActividadResponse.model_validate(actividad)


@router.patch(
    "/{actividad_id}",
    response_model=ActividadResponse,
    dependencies=[Depends(require_permission(Perm.ACTIVIDADES_GESTIONAR))],
)
async def editar_actividad(
    actividad_id: UUID,
    data: ActividadUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ActividadResponse:
    """Edita campos de una actividad existente."""
    service = ActividadService.create(db, current_user.tenant_id)
    actividad = await service.editar(actividad_id, data)
    await db.commit()
    await db.refresh(actividad)
    return ActividadResponse.model_validate(actividad)


@router.delete(
    "/{actividad_id}",
    status_code=204,
    dependencies=[Depends(require_permission(Perm.ACTIVIDADES_GESTIONAR))],
)
async def eliminar_actividad(
    actividad_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft-delete de una actividad."""
    service = ActividadService.create(db, current_user.tenant_id)
    await service.eliminar(actividad_id)
    await db.commit()


@router.get(
    "/{actividad_id}/plantilla-csv",
    dependencies=[
        Depends(
            require_permission(Perm.ACTIVIDADES_GESTIONAR)
        )
    ],
)
async def descargar_plantilla_csv(
    actividad_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Descarga plantilla CSV pre-cargada con los alumnos del padrón activo.

    Columnas: entrada_padron_id, usuario_id, nombre, apellido, nota, aprobado.
    El profesor completa nota y aprobado, luego sube el archivo.
    Gate: actividades:gestionar (PROFESOR tiene es_propio=True).
    """
    service = ActividadService.create(db, current_user.tenant_id)
    content = await service.generar_plantilla_csv(actividad_id)
    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=plantilla_{actividad_id}.csv"
        },
    )


@router.post(
    "/{actividad_id}/calificaciones-csv",
    dependencies=[
        Depends(
            require_permission(Perm.CALIFICACIONES_IMPORTAR)
        )
    ],
)
async def subir_calificaciones_csv(
    actividad_id: UUID,
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Sube un CSV con notas y aprobado para cada alumno de la actividad.

    Formato esperado: entrada_padron_id, usuario_id, nombre, apellido, nota, aprobado
    Upsert: si ya existe Calificacion para (entrada_padron_id, actividad_id) se actualiza.
    Gate: calificaciones:importar (PROFESOR tiene es_propio=True).
    """
    content = await file.read()
    service = ActividadService.create(db, current_user.tenant_id)
    result = await service.importar_calificaciones_csv(actividad_id, content)
    await db.commit()
    return result


# ── Modal individual calificacion ─────────────────────────────────────────────


class CalificacionIndividualRequest(BaseModel):
    """Request para registrar/actualizar una calificación vía modal.

    Upsert por (tenant, entrada_padron_id, actividad_id).
    origen='Manual'. Pydantic extra='forbid'.
    """
    model_config = ConfigDict(extra="forbid")

    entrada_padron_id: UUID
    nota_numerica: float | None = None
    nota_textual: str | None = None
    aprobado: bool


@router.post(
    "/{actividad_id}/calificaciones",
    status_code=201,
    dependencies=[Depends(require_permission(Perm.CALIFICACIONES_EDITAR))],
)
async def registrar_calificacion_individual(
    actividad_id: UUID,
    body: CalificacionIndividualRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Registra o actualiza una calificación individual (modal, origen=Manual).

    Upsert por (tenant, entrada_padron_id, actividad_id).
    Valida que la entrada de padrón pertenezca al dictado de la actividad y al tenant.
    Gate: calificaciones:editar (PROFESOR tiene es_propio=True).
    """
    service = ActividadService.create(db, current_user.tenant_id)
    calificacion = await service.registrar_calificacion(
        actividad_id=actividad_id,
        entrada_padron_id=body.entrada_padron_id,
        nota_numerica=body.nota_numerica,
        nota_textual=body.nota_textual,
        aprobado=body.aprobado,
        actor_user_id=current_user.user_id,
    )
    await db.commit()
    await db.refresh(calificacion)
    return {
        "id": calificacion.id,
        "entrada_padron_id": calificacion.entrada_padron_id,
        "actividad_id": calificacion.actividad_id,
        "actividad": calificacion.actividad,
        "nota_numerica": float(calificacion.nota_numerica) if calificacion.nota_numerica is not None else None,
        "nota_textual": calificacion.nota_textual,
        "aprobado": calificacion.aprobado,
        "origen": calificacion.origen,
    }
