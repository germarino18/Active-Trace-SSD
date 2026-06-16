from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.core.dependencies import get_db
from app.core.permissions import Perm
from app.core.template_engine import TemplateEngine
from app.schemas.auth import CurrentUser
from app.schemas.comunicaciones import (
    ComunicacionPreview,
    ComunicacionPreviewRequest,
    ComunicacionRead,
    EnvioMasivoRequest,
    EnvioMasivoResponse,
    LoteResumen,
)
from app.services.comunicaciones_service import ComunicacionesService

router = APIRouter(prefix="/api/v1/comunicaciones", tags=["comunicaciones"])

_allowed_template_vars = {"alumno_nombre", "alumno_apellido", "materia", "docente_nombre"}
_template_engine = TemplateEngine(allowed_variables=_allowed_template_vars)


@router.post("/preview", response_model=ComunicacionPreview)
async def preview_comunicacion(
    req: ComunicacionPreviewRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Preview a communication with template variable substitution."""
    service = ComunicacionesService.create(db, current_user.tenant_id)
    return await service.preview(
        template_engine=_template_engine,
        asunto_template=req.asunto_template,
        cuerpo_template=req.cuerpo_template,
        destinatario_info={
            "alumno_nombre": req.destinatario_nombre,
            "alumno_apellido": req.destinatario_apellido,
            "materia": req.materia_nombre,
            "docente_nombre": req.docente_nombre,
        },
    )


@router.post(
    "/enviar",
    response_model=EnvioMasivoResponse,
    dependencies=[Depends(require_permission(Perm.COMUNICACION_ENVIAR))],
)
async def enviar_masivo(
    req: EnvioMasivoRequest,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Enqueue mass communication."""
    service = ComunicacionesService.create(db, current_user.tenant_id)
    return await service.enqueue_masivo(
        envio_data=req,
        current_user=current_user,
        request=request,
    )


@router.get(
    "/{comunicacion_id}",
    response_model=ComunicacionRead,
    dependencies=[Depends(require_permission(Perm.COMUNICACION_ENVIAR))],
)
async def get_comunicacion(
    comunicacion_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get individual communication status."""
    service = ComunicacionesService.create(db, current_user.tenant_id)
    return await service.get_estado(comunicacion_id)


@router.get(
    "/lotes/{lote_id}",
    response_model=LoteResumen,
    dependencies=[Depends(require_permission(Perm.COMUNICACION_ENVIAR))],
)
async def get_resumen_lote(
    lote_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get batch summary for a communication lot."""
    service = ComunicacionesService.create(db, current_user.tenant_id)
    return await service.get_resumen_lote(lote_id)


@router.post(
    "/{comunicacion_id}/aprobar",
    dependencies=[Depends(require_permission(Perm.COMUNICACION_APROBAR))],
)
async def aprobar_comunicacion(
    comunicacion_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Approve a single communication."""
    service = ComunicacionesService.create(db, current_user.tenant_id)
    await service.aprobar_individual(comunicacion_id, current_user=current_user, request=request)
    return {"status": "ok"}


@router.post(
    "/lotes/{lote_id}/aprobar",
    dependencies=[Depends(require_permission(Perm.COMUNICACION_APROBAR))],
)
async def aprobar_lote(
    lote_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Approve an entire batch."""
    service = ComunicacionesService.create(db, current_user.tenant_id)
    await service.aprobar_lote(lote_id, current_user=current_user, request=request)
    return {"status": "ok"}


@router.post(
    "/{comunicacion_id}/cancelar",
    dependencies=[Depends(require_permission(Perm.COMUNICACION_APROBAR))],
)
async def cancelar_comunicacion(
    comunicacion_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Cancel a single communication."""
    service = ComunicacionesService.create(db, current_user.tenant_id)
    await service.cancelar_individual(comunicacion_id, current_user=current_user, request=request)
    return {"status": "ok"}


@router.post(
    "/lotes/{lote_id}/cancelar",
    dependencies=[Depends(require_permission(Perm.COMUNICACION_APROBAR))],
)
async def cancelar_lote(
    lote_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Cancel an entire batch."""
    service = ComunicacionesService.create(db, current_user.tenant_id)
    await service.cancelar_lote(lote_id, current_user=current_user, request=request)
    return {"status": "ok"}
