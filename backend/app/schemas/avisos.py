"""Pydantic schemas for avisos (announcements with acknowledgment)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from pydantic.functional_validators import BeforeValidator
from typing import Annotated

from app.models.aviso import AlcanceAviso, SeveridadAviso


def _validate_alcance(v: str) -> str:
    if v not in (e.value for e in AlcanceAviso):
        raise ValueError(f"Invalid alcance: {v}")
    return v


def _validate_severidad(v: str) -> str:
    if v not in (e.value for e in SeveridadAviso):
        raise ValueError(f"Invalid severidad: {v}")
    return v


AlcanceField = Annotated[str, BeforeValidator(_validate_alcance)]
SeveridadField = Annotated[str, BeforeValidator(_validate_severidad)]


class AvisoCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alcance: AlcanceField
    materia_id: UUID | None = None
    cohorte_id: UUID | None = None
    rol_destino: str | None = None
    severidad: SeveridadField = SeveridadAviso.INFO.value
    titulo: str = Field(..., min_length=1, max_length=255)
    cuerpo: str = Field(..., min_length=1)
    inicio_en: datetime
    fin_en: datetime
    orden: int = 0
    activo: bool = True
    requiere_ack: bool = False


class AvisoUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alcance: AlcanceField | None = None
    materia_id: UUID | None = None
    cohorte_id: UUID | None = None
    rol_destino: str | None = None
    severidad: SeveridadField | None = None
    titulo: str | None = Field(None, min_length=1, max_length=255)
    cuerpo: str | None = Field(None, min_length=1)
    inicio_en: datetime | None = None
    fin_en: datetime | None = None
    orden: int | None = None
    activo: bool | None = None
    requiere_ack: bool | None = None


class AvisoRead(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    tenant_id: UUID
    alcance: str
    materia_id: UUID | None = None
    cohorte_id: UUID | None = None
    rol_destino: str | None = None
    severidad: str
    titulo: str
    cuerpo: str
    inicio_en: datetime
    fin_en: datetime
    orden: int
    activo: bool
    requiere_ack: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class AvisoVisibleRead(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    tenant_id: UUID
    alcance: str
    materia_id: UUID | None = None
    cohorte_id: UUID | None = None
    rol_destino: str | None = None
    severidad: str
    titulo: str
    cuerpo: str
    inicio_en: datetime
    fin_en: datetime
    orden: int
    activo: bool
    requiere_ack: bool
    acknowledged: bool = False
    created_at: datetime
    updated_at: datetime


class AcknowledgmentRead(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    aviso_id: UUID
    usuario_id: UUID
    confirmado_at: datetime


class AcknowledgmentStats(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total: int
    confirmados: int
    pendientes: int


class ConfirmResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    acknowledged: bool


class AvisoListParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=200)
    activo: bool | None = None
    alcance: str | None = None
