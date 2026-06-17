"""Router for liquidaciones (salary settlements) API."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.core.dependencies import get_db
from app.core.permissions import Perm
from app.schemas.auth import CurrentUser
from app.schemas.liquidaciones import (
    ClavePlusCreate,
    ClavePlusRead,
    ClavePlusUpdate,
    LiquidacionCalcularRequest,
    LiquidacionCerrarResponse,
    LiquidacionHistorialParams,
    LiquidacionPeriodoResponse,
    MateriaClavePlusCreate,
    MateriaClavePlusRead,
    SalarioBaseCreate,
    SalarioBaseRead,
    SalarioBaseUpdate,
    SalarioPlusCreate,
    SalarioPlusRead,
    SalarioPlusUpdate,
)
from app.services.liquidacion_service import LiquidacionService
from app.services.grilla_salarial_service import GrillaSalarialService
from app.services.clave_plus_service import ClavePlusService

router = APIRouter(prefix="/api/v1/liquidaciones", tags=["liquidaciones"])


# ── Liquidaciones ────────────────────────────────────────────────────


@router.get("", response_model=LiquidacionPeriodoResponse, dependencies=[Depends(require_permission(Perm.LIQUIDACIONES_CERRAR))])
async def ver_liquidaciones(
    periodo: str = Query(..., pattern=r"^\d{4}-\d{2}$"),
    cohorte_id: UUID = Query(...),
    usuario_id: UUID | None = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get segmented view of liquidations for a period."""
    service = LiquidacionService.create(db, current_user.tenant_id)
    return await service.obtener_vista_periodo(
        periodo=periodo,
        cohorte_id=cohorte_id,
        usuario_id=usuario_id,
    )


@router.get("/historial", response_model=list, dependencies=[Depends(require_permission(Perm.LIQUIDACIONES_CERRAR))])
async def historial_liquidaciones(
    cohorte_id: UUID | None = Query(None),
    desde: str | None = Query(None, pattern=r"^\d{4}-\d{2}$"),
    hasta: str | None = Query(None, pattern=r"^\d{4}-\d{2}$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get history of closed liquidations."""
    service = LiquidacionService.create(db, current_user.tenant_id)
    return await service.obtener_historial(
        cohorte_id=cohorte_id,
        desde=desde,
        hasta=hasta,
        skip=skip,
        limit=limit,
    )


@router.post("/calcular", response_model=LiquidacionPeriodoResponse, status_code=201, dependencies=[Depends(require_permission(Perm.LIQUIDACIONES_CERRAR))])
async def calcular_liquidaciones(
    req: LiquidacionCalcularRequest,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Calculate/recalculate salary settlements for a period."""
    service = LiquidacionService.create(db, current_user.tenant_id)
    return await service.calcular_periodo(
        periodo=req.periodo,
        cohorte_id=req.cohorte_id,
        current_user=current_user,
        request=request,
    )


@router.post("/{liquidacion_id}/cerrar", response_model=LiquidacionCerrarResponse, dependencies=[Depends(require_permission(Perm.LIQUIDACIONES_CERRAR))])
async def cerrar_liquidacion(
    liquidacion_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Close a liquidacion (immutable)."""
    service = LiquidacionService.create(db, current_user.tenant_id)
    return await service.cerrar(
        liquidacion_id=liquidacion_id,
        current_user=current_user,
        request=request,
    )


# ── Salario Base CRUD ────────────────────────────────────────────────


@router.get("/salarios-base", response_model=list[SalarioBaseRead], dependencies=[Depends(require_permission(Perm.LIQUIDACIONES_CERRAR))])
async def listar_salarios_base(
    rol: str | None = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List SalarioBase entries."""
    service = GrillaSalarialService.create(db, current_user.tenant_id)
    return await service.listar_bases(rol=rol)


@router.post("/salarios-base", response_model=SalarioBaseRead, status_code=201, dependencies=[Depends(require_permission(Perm.LIQUIDACIONES_CERRAR))])
async def crear_salario_base(
    req: SalarioBaseCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new SalarioBase entry."""
    service = GrillaSalarialService.create(db, current_user.tenant_id)
    return await service.crear_base(req)


@router.get("/salarios-base/{id}", response_model=SalarioBaseRead, dependencies=[Depends(require_permission(Perm.LIQUIDACIONES_CERRAR))])
async def obtener_salario_base(
    id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single SalarioBase entry."""
    service = GrillaSalarialService.create(db, current_user.tenant_id)
    return await service.obtener_base(id)


@router.patch("/salarios-base/{id}", response_model=SalarioBaseRead, dependencies=[Depends(require_permission(Perm.LIQUIDACIONES_CERRAR))])
async def actualizar_salario_base(
    id: UUID,
    req: SalarioBaseUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a SalarioBase entry."""
    service = GrillaSalarialService.create(db, current_user.tenant_id)
    return await service.actualizar_base(id, req)


@router.delete("/salarios-base/{id}", status_code=204, dependencies=[Depends(require_permission(Perm.LIQUIDACIONES_CERRAR))])
async def eliminar_salario_base(
    id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a SalarioBase entry."""
    service = GrillaSalarialService.create(db, current_user.tenant_id)
    await service.eliminar_base(id)


# ── Salario Plus CRUD ────────────────────────────────────────────────


@router.get("/salarios-plus", response_model=list[SalarioPlusRead], dependencies=[Depends(require_permission(Perm.LIQUIDACIONES_CERRAR))])
async def listar_salarios_plus(
    grupo: str | None = Query(None),
    rol: str | None = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List SalarioPlus entries."""
    service = GrillaSalarialService.create(db, current_user.tenant_id)
    return await service.listar_plus(grupo=grupo, rol=rol)


@router.post("/salarios-plus", response_model=SalarioPlusRead, status_code=201, dependencies=[Depends(require_permission(Perm.LIQUIDACIONES_CERRAR))])
async def crear_salario_plus(
    req: SalarioPlusCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new SalarioPlus entry."""
    service = GrillaSalarialService.create(db, current_user.tenant_id)
    return await service.crear_plus(req)


@router.get("/salarios-plus/{id}", response_model=SalarioPlusRead, dependencies=[Depends(require_permission(Perm.LIQUIDACIONES_CERRAR))])
async def obtener_salario_plus(
    id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single SalarioPlus entry."""
    service = GrillaSalarialService.create(db, current_user.tenant_id)
    return await service.obtener_plus(id)


@router.patch("/salarios-plus/{id}", response_model=SalarioPlusRead, dependencies=[Depends(require_permission(Perm.LIQUIDACIONES_CERRAR))])
async def actualizar_salario_plus(
    id: UUID,
    req: SalarioPlusUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a SalarioPlus entry."""
    service = GrillaSalarialService.create(db, current_user.tenant_id)
    return await service.actualizar_plus(id, req)


@router.delete("/salarios-plus/{id}", status_code=204, dependencies=[Depends(require_permission(Perm.LIQUIDACIONES_CERRAR))])
async def eliminar_salario_plus(
    id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a SalarioPlus entry."""
    service = GrillaSalarialService.create(db, current_user.tenant_id)
    await service.eliminar_plus(id)


# ── ClavePlus CRUD ───────────────────────────────────────────────────


@router.get("/claves-plus", response_model=list[ClavePlusRead], dependencies=[Depends(require_permission(Perm.LIQUIDACIONES_CERRAR))])
async def listar_claves_plus(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List ClavePlus entries."""
    service = ClavePlusService.create(db, current_user.tenant_id)
    return await service.listar_claves()


@router.post("/claves-plus", response_model=ClavePlusRead, status_code=201, dependencies=[Depends(require_permission(Perm.LIQUIDACIONES_CERRAR))])
async def crear_clave_plus(
    req: ClavePlusCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new ClavePlus entry."""
    service = ClavePlusService.create(db, current_user.tenant_id)
    return await service.crear_clave(req)


@router.get("/claves-plus/{id}", response_model=ClavePlusRead, dependencies=[Depends(require_permission(Perm.LIQUIDACIONES_CERRAR))])
async def obtener_clave_plus(
    id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single ClavePlus entry."""
    service = ClavePlusService.create(db, current_user.tenant_id)
    return await service.obtener_clave(id)


@router.patch("/claves-plus/{id}", response_model=ClavePlusRead, dependencies=[Depends(require_permission(Perm.LIQUIDACIONES_CERRAR))])
async def actualizar_clave_plus(
    id: UUID,
    req: ClavePlusUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a ClavePlus entry."""
    service = ClavePlusService.create(db, current_user.tenant_id)
    return await service.actualizar_clave(id, req)


@router.delete("/claves-plus/{id}", status_code=204, dependencies=[Depends(require_permission(Perm.LIQUIDACIONES_CERRAR))])
async def eliminar_clave_plus(
    id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a ClavePlus entry."""
    service = ClavePlusService.create(db, current_user.tenant_id)
    await service.eliminar_clave(id)


# ── MateriaClavePlus CRUD ────────────────────────────────────────────


@router.get("/materias-clave-plus", response_model=list[MateriaClavePlusRead], dependencies=[Depends(require_permission(Perm.LIQUIDACIONES_CERRAR))])
async def listar_materias_clave_plus(
    materia_id: UUID | None = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List MateriaClavePlus entries."""
    service = ClavePlusService.create(db, current_user.tenant_id)
    return await service.listar_materias_clave(materia_id=materia_id)


@router.post("/materias-clave-plus", response_model=MateriaClavePlusRead, status_code=201, dependencies=[Depends(require_permission(Perm.LIQUIDACIONES_CERRAR))])
async def crear_materia_clave_plus(
    req: MateriaClavePlusCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new MateriaClavePlus entry."""
    service = ClavePlusService.create(db, current_user.tenant_id)
    return await service.crear_materia_clave(req)


@router.delete("/materias-clave-plus/{id}", status_code=204, dependencies=[Depends(require_permission(Perm.LIQUIDACIONES_CERRAR))])
async def eliminar_materia_clave_plus(
    id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a MateriaClavePlus entry."""
    service = ClavePlusService.create(db, current_user.tenant_id)
    await service.eliminar_materia_clave(id)
