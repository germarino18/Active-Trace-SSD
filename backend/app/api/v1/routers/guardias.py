from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.core.dependencies import get_db
from app.core.permissions import Perm
from app.schemas.auth import CurrentUser
from app.schemas.guardias import GuardiaCreate, GuardiaRead, GuardiaUpdate
from app.services.guardias import GuardiasService

router = APIRouter(
    prefix="/api/v1/guardias", tags=["guardias"],
    dependencies=[Depends(require_permission(Perm.ENCUENTROS_GESTIONAR))],
)


@router.post("", response_model=GuardiaRead, status_code=201)
async def registrar_guardia(
    data: GuardiaCreate,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Register a new guardia."""
    service = GuardiasService.create(db, current_user.tenant_id)
    return await service.registrar(data, current_user=current_user, request=request)


@router.get("", response_model=list[GuardiaRead])
async def listar_guardias(
    asignacion_id: UUID | None = Query(None),
    dictado_id: UUID | None = Query(None),
    estado: str | None = Query(None),
    dia: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List guardias with optional filters."""
    service = GuardiasService.create(db, current_user.tenant_id)
    return await service.listar(
        asignacion_id=asignacion_id,
        dictado_id=dictado_id,
        estado=estado,
        dia=dia,
        skip=skip,
        limit=limit,
    )


@router.get("/export", include_in_schema=False)
async def exportar_guardias(
    dictado_id: UUID | None = Query(None),
    asignacion_id: UUID | None = Query(None),
    estado: str | None = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export guardias to CSV (F6.6)."""
    service = GuardiasService.create(db, current_user.tenant_id)
    return await service.exportar_csv(
        dictado_id=dictado_id,
        asignacion_id=asignacion_id,
        estado=estado,
    )


@router.get("/{guardia_id}", response_model=GuardiaRead)
async def obtener_guardia(
    guardia_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get guardia details."""
    service = GuardiasService.create(db, current_user.tenant_id)
    return await service.obtener(guardia_id)


@router.put("/{guardia_id}", response_model=GuardiaRead)
async def editar_guardia(
    guardia_id: UUID,
    data: GuardiaUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Edit guardia (estado, comentarios)."""
    service = GuardiasService.create(db, current_user.tenant_id)
    return await service.editar(guardia_id, data, current_user=current_user, request=request)
