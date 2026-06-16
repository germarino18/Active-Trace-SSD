from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProgramaMateriaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dictado_id: UUID
    titulo: str = Field(..., min_length=1)


class ProgramaMateriaRead(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    dictado_id: UUID
    titulo: str
    referencia_archivo: str
    cargado_at: datetime
    created_at: datetime
    updated_at: datetime


class ProgramaMateriaUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    titulo: str | None = None
