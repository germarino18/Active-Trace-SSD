from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FechaAcademicaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dictado_id: UUID
    tipo: str = Field(..., pattern=r"^(Parcial|TP|Coloquio|Recuperatorio)$")
    numero: int = Field(..., ge=1)
    periodo: str = Field(..., min_length=1)
    fecha: datetime
    titulo: str


class FechaAcademicaRead(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    dictado_id: UUID
    tipo: str
    numero: int
    periodo: str
    fecha: datetime
    titulo: str
    created_at: datetime
    updated_at: datetime


class FechaAcademicaUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tipo: str | None = Field(None, pattern=r"^(Parcial|TP|Coloquio|Recuperatorio)$")
    numero: int | None = Field(None, ge=1)
    periodo: str | None = Field(None, min_length=1)
    fecha: datetime | None = None
    titulo: str | None = None


class FechaAcademicaFilterParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dictado_id: UUID
    periodo: str | None = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=500)


class LmsContentFragment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contenido: str
