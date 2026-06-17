"""Router for facturas (invoices from teachers who invoice) API."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.core.dependencies import get_db
from app.core.permissions import Perm
from app.schemas.auth import CurrentUser
from app.schemas.facturas import (
    FacturaAbonarResponse,
    FacturaCreate,
    FacturaListParams,
    FacturaRead,
    FacturaUpdate,
)
from app.services.factura_service import FacturaService

router = APIRouter(prefix="/api/v1/facturas", tags=["facturas"])


@router.get("", response_model=list[FacturaRead], dependencies=[Depends(require_permission(Perm.FACTURAS_GESTIONAR))])
async def listar_facturas(
    usuario_id: UUID | None = Query(None),
    periodo: str | None = Query(None, pattern=r"^\d{4}-\d{2}$"),
    estado: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List facturas with filters."""
    params = FacturaListParams(
        usuario_id=usuario_id,
        periodo=periodo,
        estado=estado,
        skip=skip,
        limit=limit,
    )
    service = FacturaService.create(db, current_user.tenant_id)
    return await service.listar(params)


@router.post("", response_model=FacturaRead, status_code=201, dependencies=[Depends(require_permission(Perm.FACTURAS_GESTIONAR))])
async def crear_factura(
    req: FacturaCreate,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Create a new factura."""
    service = FacturaService.create(db, current_user.tenant_id)
    return await service.crear(data=req, current_user=current_user, request=request)


@router.get("/{factura_id}", response_model=FacturaRead, dependencies=[Depends(require_permission(Perm.FACTURAS_GESTIONAR))])
async def obtener_factura(
    factura_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single factura."""
    service = FacturaService.create(db, current_user.tenant_id)
    return await service.obtener(factura_id)


@router.patch("/{factura_id}", response_model=FacturaRead, dependencies=[Depends(require_permission(Perm.FACTURAS_GESTIONAR))])
async def actualizar_factura(
    factura_id: UUID,
    req: FacturaUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Update a factura."""
    service = FacturaService.create(db, current_user.tenant_id)
    update_data = {k: v for k, v in req.model_dump().items() if v is not None}
    return await service.actualizar(
        factura_id,
        data=update_data,
        current_user=current_user,
        request=request,
    )


@router.post("/{factura_id}/abonar", response_model=FacturaAbonarResponse, dependencies=[Depends(require_permission(Perm.FACTURAS_GESTIONAR))])
async def abonar_factura(
    factura_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Mark a factura as paid."""
    service = FacturaService.create(db, current_user.tenant_id)
    return await service.abonar(
        factura_id,
        current_user=current_user,
        request=request,
    )


@router.delete("/{factura_id}", status_code=204, dependencies=[Depends(require_permission(Perm.FACTURAS_GESTIONAR))])
async def eliminar_factura(
    factura_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a factura."""
    service = FacturaService.create(db, current_user.tenant_id)
    await service.eliminar(
        factura_id,
        current_user=current_user,
        request=request,
    )
