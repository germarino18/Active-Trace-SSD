from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EvaluacionMateriaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    materia_id: UUID
    cohorte_id: UUID | None = None
    tipo: str = Field(..., max_length=30)
    instancia: int = Field(..., ge=1)
    fecha: date
    titulo: str | None = Field(default=None, max_length=255)


class EvaluacionMateriaUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tipo: str | None = Field(default=None, max_length=30)
    instancia: int | None = Field(default=None, ge=1)
    fecha: date | None = None
    titulo: str | None = Field(default=None, max_length=255)


class EvaluacionMateriaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID
    materia_id: UUID
    cohorte_id: UUID | None = None
    tipo: str
    instancia: int
    fecha: date
    titulo: str | None = None
    deleted_at: bool = False
