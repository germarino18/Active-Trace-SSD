"""Pydantic schemas for liquidaciones (salary settlements) module."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ── SalarioBase ─────────────────────────────────────────────────────


class SalarioBaseCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rol: str = Field(..., min_length=1, max_length=30)
    monto: Decimal = Field(..., gt=0, decimal_places=2)
    desde: date
    hasta: date | None = None


class SalarioBaseUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rol: str | None = Field(None, min_length=1, max_length=30)
    monto: Decimal | None = Field(None, gt=0, decimal_places=2)
    desde: date | None = None
    hasta: date | None = None


class SalarioBaseRead(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    tenant_id: UUID
    rol: str
    monto: Decimal
    desde: date
    hasta: date | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


# ── SalarioPlus ─────────────────────────────────────────────────────


class SalarioPlusCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    grupo: str = Field(..., min_length=1, max_length=50)
    rol: str = Field(..., min_length=1, max_length=30)
    descripcion: str = Field(..., min_length=1, max_length=255)
    monto: Decimal = Field(..., gt=0, decimal_places=2)
    desde: date
    hasta: date | None = None


class SalarioPlusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    grupo: str | None = Field(None, min_length=1, max_length=50)
    rol: str | None = Field(None, min_length=1, max_length=30)
    descripcion: str | None = Field(None, min_length=1, max_length=255)
    monto: Decimal | None = Field(None, gt=0, decimal_places=2)
    desde: date | None = None
    hasta: date | None = None


class SalarioPlusRead(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    tenant_id: UUID
    grupo: str
    rol: str
    descripcion: str
    monto: Decimal
    desde: date
    hasta: date | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


# ── ClavePlus ───────────────────────────────────────────────────────


class ClavePlusCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    codigo: str = Field(..., min_length=1, max_length=30)
    descripcion: str = Field(..., min_length=1, max_length=255)
    desde: date
    hasta: date | None = None


class ClavePlusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    codigo: str | None = Field(None, min_length=1, max_length=30)
    descripcion: str | None = Field(None, min_length=1, max_length=255)
    desde: date | None = None
    hasta: date | None = None


class ClavePlusRead(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    tenant_id: UUID
    codigo: str
    descripcion: str
    desde: date
    hasta: date | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


# ── MateriaClavePlus ────────────────────────────────────────────────


class MateriaClavePlusCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: UUID
    clave_plus_id: UUID
    desde: date
    hasta: date | None = None


class MateriaClavePlusRead(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    tenant_id: UUID
    materia_id: UUID
    clave_plus_id: UUID
    desde: date
    hasta: date | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


# ── Liquidacion ──────────────────────────────────────────────────────


class LiquidacionCalcularRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    periodo: str = Field(..., pattern=r"^\d{4}-\d{2}$")
    cohorte_id: UUID


class LiquidacionCerrarResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    estado: str
    mensaje: str


class LiquidacionRead(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    tenant_id: UUID
    cohorte_id: UUID
    periodo: str
    usuario_id: UUID
    rol: str
    comisiones: str | None = None
    monto_base: Decimal
    monto_plus: Decimal
    total: Decimal
    es_nexo: bool
    excluido_por_factura: bool
    estado: str
    created_at: datetime
    updated_at: datetime


class SegmentoLiquidacion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[LiquidacionRead]
    subtotal: Decimal


class LiquidacionPeriodoResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    periodo: str
    cohorte_id: UUID
    general: SegmentoLiquidacion
    nexo: SegmentoLiquidacion
    factura: SegmentoLiquidacion
    kpis: dict[str, Decimal]


class LiquidacionHistorialParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cohorte_id: UUID | None = None
    desde: str | None = Field(None, pattern=r"^\d{4}-\d{2}$")
    hasta: str | None = Field(None, pattern=r"^\d{4}-\d{2}$")
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=200)
