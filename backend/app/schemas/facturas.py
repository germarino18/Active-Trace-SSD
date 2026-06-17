"""Pydantic schemas for facturas (invoices from teachers who invoice)."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FacturaCreate(BaseModel):
    """Create a new factura.

    Note: `usuario_id` here is the **User.id** (auth user PK), not the
    Usuario.id. The service resolves the actual Usuario.id internally
    before persisting the FK relationship.
    """
    model_config = ConfigDict(extra="forbid")

    usuario_id: UUID
    periodo: str = Field(..., pattern=r"^\d{4}-\d{2}$")
    detalle: str | None = None
    referencia_archivo: str | None = Field(None, max_length=500)
    tamano_kb: Decimal | None = None


class FacturaUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    detalle: str | None = None
    referencia_archivo: str | None = Field(None, max_length=500)
    tamano_kb: Decimal | None = None


class FacturaRead(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    tenant_id: UUID
    usuario_id: UUID
    periodo: str
    detalle: str | None = None
    referencia_archivo: str | None = None
    tamano_kb: Decimal | None = None
    estado: str
    cargada_at: datetime
    abonada_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class FacturaAbonarResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    estado: str
    abonada_at: datetime
    mensaje: str


class FacturaListParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    usuario_id: UUID | None = None
    periodo: str | None = Field(None, pattern=r"^\d{4}-\d{2}$")
    estado: str | None = None
    desde: datetime | None = None
    hasta: datetime | None = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=200)
