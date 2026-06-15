"""Router para calificaciones (C-10 Tasks 7.1-7.8).

Endpoints:
  POST   /api/admin/calificaciones/preview              — preview archivo calificaciones
  POST   /api/admin/calificaciones/importar              — confirmar importación
  POST   /api/admin/calificaciones/preview-finalizacion  — preview finalización
  POST   /api/admin/calificaciones/importar-finalizacion — confirmar finalización
  GET    /api/admin/calificaciones/dictados/{dictado_id} — listar calificaciones
  PUT    /api/admin/calificaciones/umbral                — configurar umbral
  GET    /api/admin/calificaciones/umbral                — obtener umbral vigente
"""

from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.core.dependencies import get_db
from app.core.permissions import Perm
from app.schemas.auth import CurrentUser
from app.schemas.calificaciones import (
    CalificacionResponse,
    ImportCalificacionesConfirm,
    ImportCalificacionesResponse,
    UmbralMateriaCreate,
)
from app.services.calificaciones.calificacion_service import CalificacionService
from app.services.calificaciones.umbral_service import UmbralService

router = APIRouter(prefix="/api/admin/calificaciones", tags=["calificaciones"])


@router.post(
    "/preview",
    dependencies=[Depends(require_permission(Perm.CALIFICACIONES_IMPORTAR))],
)
async def preview_calificaciones(
    file: UploadFile = File(...),
    dictado_id: UUID = Form(...),
    current_user: CurrentUser = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db),
):
    """Previsualizar calificaciones desde archivo LMS."""
    content = await file.read()
    service = CalificacionService(db_session, current_user.tenant_id, current_user.user_id)
    return await service.preview_archivo(content, file.filename or "upload", dictado_id)


@router.post(
    "/importar",
    response_model=ImportCalificacionesResponse,
    dependencies=[Depends(require_permission(Perm.CALIFICACIONES_IMPORTAR))],
)
async def importar_calificaciones(
    body: ImportCalificacionesConfirm,
    current_user: CurrentUser = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db),
):
    """Confirmar importación de calificaciones con actividades seleccionadas."""
    service = CalificacionService(db_session, current_user.tenant_id, current_user.user_id)
    return await service.confirmar_importacion(
        body.dictado_id, body.preview_token, body.actividades_seleccionadas,
    )


@router.post(
    "/preview-finalizacion",
    dependencies=[Depends(require_permission(Perm.CALIFICACIONES_IMPORTAR))],
)
async def preview_finalizacion(
    file: UploadFile = File(...),
    dictado_id: UUID = Form(...),
    current_user: CurrentUser = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db),
):
    """Previsualizar reporte de finalización."""
    content = await file.read()
    service = CalificacionService(db_session, current_user.tenant_id, current_user.user_id)
    return await service.importar_finalizacion_preview(content, file.filename or "upload", dictado_id)


@router.post(
    "/importar-finalizacion",
    dependencies=[Depends(require_permission(Perm.CALIFICACIONES_IMPORTAR))],
)
async def importar_finalizacion(
    body: ImportCalificacionesConfirm,
    current_user: CurrentUser = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db),
):
    """Confirmar importación de finalización."""
    service = CalificacionService(db_session, current_user.tenant_id, current_user.user_id)
    return await service.importar_finalizacion_confirm(body.dictado_id, body.preview_token)


@router.get(
    "/dictados/{dictado_id}",
    response_model=list[CalificacionResponse],
    dependencies=[Depends(require_permission(Perm.CALIFICACIONES_IMPORTAR))],
)
async def listar_calificaciones(
    dictado_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db),
):
    """Listar calificaciones de un dictado."""
    service = CalificacionService(db_session, current_user.tenant_id, current_user.user_id)
    return await service.listar_calificaciones(dictado_id)


@router.put(
    "/umbral",
    dependencies=[Depends(require_permission(Perm.CALIFICACIONES_IMPORTAR))],
)
async def configurar_umbral(
    body: UmbralMateriaCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db),
):
    """Configurar umbral de aprobación para un dictado."""
    service = UmbralService(db_session, current_user.tenant_id, current_user.user_id)
    return await service.configurar_umbral(body.dictado_id, body.umbral_pct, body.valores_aprobatorios)


@router.get(
    "/umbral",
    dependencies=[Depends(require_permission(Perm.CALIFICACIONES_IMPORTAR))],
)
async def obtener_umbral(
    dictado_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db),
):
    """Obtener umbral vigente para un dictado."""
    service = UmbralService(db_session, current_user.tenant_id, current_user.user_id)
    return await service.obtener_umbral(dictado_id)
