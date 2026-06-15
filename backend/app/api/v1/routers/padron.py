"""Router para operaciones de padrón (C-09 Tasks 7.1-7.2).

Endpoints:
  POST   /api/admin/padron/preview          — previsualizar archivo
  POST   /api/admin/padron/importar          — confirmar importación
  GET    /api/admin/padron/dictados/{id}     — padrón activo
  GET    /api/admin/padron/versiones         — historial de versiones
  POST   /api/admin/padron/dictados/{id}/vaciar — vaciar dictado (RN-04)
  POST   /api/admin/padron/sync/moodle       — sincronizar desde Moodle

Todos los endpoints siguen el patrón Routers → Services → Repositories
(regla dura #11). Identidad y tenant salen de la sesión (reglas #8/#9).
"""

from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.core.dependencies import get_db
from app.core.permissions import Perm
from app.schemas.auth import CurrentUser
from app.schemas.padron import (
    EntradaPadronResponse,
    PadronImportConfirm,
    PadronImportResponse,
    PadronPreviewResponse,
    PadronVaciarResponse,
    VersionPadronHistoryResponse,
)
from app.services.padron.moodle_sync_service import MoodleSyncService
from app.services.padron.padron_service import PadronService

router = APIRouter(prefix="/api/admin/padron", tags=["padron"])


class MoodleSyncRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    dictado_id: UUID
    base_url: str
    token: str
    course_id: int


@router.post(
    "/preview",
    response_model=PadronPreviewResponse,
    dependencies=[Depends(require_permission(Perm.PADRON_IMPORTAR))],
)
async def preview_padron(
    file: UploadFile = File(...),
    dictado_id: UUID = Form(...),
    current_user: CurrentUser = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db),
):
    """Previsualizar un archivo de padrón antes de importar."""
    content = await file.read()
    service = PadronService(db_session, current_user.tenant_id, current_user.user_id)
    return await service.preview_archivo(content, file.filename or "upload", dictado_id)


@router.post(
    "/importar",
    response_model=PadronImportResponse,
    dependencies=[Depends(require_permission(Perm.PADRON_IMPORTAR))],
)
async def importar_padron(
    body: PadronImportConfirm,
    current_user: CurrentUser = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db),
):
    """Confirmar importación después de previsualizar."""
    service = PadronService(db_session, current_user.tenant_id, current_user.user_id)
    return await service.confirmar_importacion(body.dictado_id, body.preview_token)


@router.get(
    "/dictados/{dictado_id}",
    response_model=list[EntradaPadronResponse],
    dependencies=[Depends(require_permission(Perm.PADRON_VER))],
)
async def obtener_padron(
    dictado_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db),
):
    """Obtener el padrón activo para un dictado."""
    service = PadronService(db_session, current_user.tenant_id, current_user.user_id)
    return await service.obtener_padron_activo(dictado_id)


@router.get(
    "/versiones",
    response_model=VersionPadronHistoryResponse,
    dependencies=[Depends(require_permission(Perm.PADRON_VER))],
)
async def listar_versiones(
    dictado_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db),
):
    """Listar el historial de versiones para un dictado."""
    service = PadronService(db_session, current_user.tenant_id, current_user.user_id)
    versiones = await service.listar_versiones(dictado_id)
    return VersionPadronHistoryResponse(versiones=versiones)


@router.post(
    "/dictados/{dictado_id}/vaciar",
    response_model=PadronVaciarResponse,
    dependencies=[Depends(require_permission(Perm.PADRON_VACIAR))],
)
async def vaciar_dictado(
    dictado_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db),
):
    """Vaciar datos de dictado (scope-isolated per RN-04).

    Coordinadores borran todos los datos del dictado.
    Profesores borran solo sus propias versiones.
    """
    es_coordinador = "COORDINADOR" in current_user.roles
    service = PadronService(db_session, current_user.tenant_id, current_user.user_id)
    return await service.vaciar_dictado(dictado_id, current_user.user_id, es_coordinador)


@router.post(
    "/sync/moodle",
    dependencies=[Depends(require_permission(Perm.PADRON_IMPORTAR))],
)
async def sync_moodle(
    body: MoodleSyncRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db),
):
    """Sincronizar padrón desde Moodle on-demand."""
    sync_service = MoodleSyncService(db_session, current_user.tenant_id, current_user.user_id)
    moodle_config = {
        "base_url": body.base_url,
        "token": body.token,
        "course_id": body.course_id,
    }
    return await sync_service.sync_on_demand(body.dictado_id, moodle_config)
