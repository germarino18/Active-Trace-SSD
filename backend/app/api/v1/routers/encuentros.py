from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.core.dependencies import get_db
from app.core.permissions import Perm
from app.schemas.auth import CurrentUser
from app.schemas.encuentros import (
    BloqueHTMLResponse,
    InstanciaEncuentroCreate,
    InstanciaEncuentroRead,
    InstanciaEncuentroUpdate,
    SlotEncuentroCreate,
    SlotEncuentroRead,
    SlotEncuentroUpdate,
)
from app.services.encuentros import EncuentrosService

router = APIRouter(
    prefix="/api/v1/encuentros", tags=["encuentros"],
    dependencies=[Depends(require_permission(Perm.ENCUENTROS_GESTIONAR))],
)


@router.post("/slots", response_model=SlotEncuentroRead, status_code=201)
async def crear_slot(
    data: SlotEncuentroCreate,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Create a recurrent or single encounter slot."""
    service = EncuentrosService.create(db, current_user.tenant_id)
    return await service.crear_slot(data, current_user=current_user, request=request)


@router.get("/slots/{slot_id}", response_model=SlotEncuentroRead)
async def obtener_slot(
    slot_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get slot details."""
    service = EncuentrosService.create(db, current_user.tenant_id)
    return await service.obtener_slot(slot_id)


@router.put("/slots/{slot_id}", response_model=SlotEncuentroRead)
async def actualizar_slot(
    slot_id: UUID,
    data: SlotEncuentroUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update slot metadata."""
    service = EncuentrosService.create(db, current_user.tenant_id)
    return await service.actualizar_slot(slot_id, data)


@router.delete("/slots/{slot_id}", status_code=204)
async def eliminar_slot(
    slot_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft delete a slot."""
    service = EncuentrosService.create(db, current_user.tenant_id)
    await service.eliminar_slot(slot_id)


@router.get("/instancias", response_model=list[InstanciaEncuentroRead])
async def listar_instancias(
    dictado_id: UUID | None = Query(None),
    estado: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List encounter instances with optional filters."""
    service = EncuentrosService.create(db, current_user.tenant_id)
    return await service.listar_instancias(
        dictado_id=dictado_id,
        estado=estado,
        skip=skip,
        limit=limit,
    )


@router.get("/instancias/{instancia_id}", response_model=InstanciaEncuentroRead)
async def obtener_instancia(
    instancia_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get instance details."""
    service = EncuentrosService.create(db, current_user.tenant_id)
    return await service.obtener_instancia(instancia_id)


@router.put("/instancias/{instancia_id}", response_model=InstanciaEncuentroRead)
async def editar_instancia(
    instancia_id: UUID,
    data: InstanciaEncuentroUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Edit instance (state, meet_url, video_url, comentario)."""
    service = EncuentrosService.create(db, current_user.tenant_id)
    return await service.editar_instancia(
        instancia_id, data, current_user=current_user, request=request
    )


@router.get("/bloque-html", response_model=BloqueHTMLResponse)
async def generar_bloque_html(
    dictado_id: UUID = Query(...),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate HTML block for LMS (F6.4)."""
    service = EncuentrosService.create(db, current_user.tenant_id)
    return await service.generar_bloque_html(dictado_id)
