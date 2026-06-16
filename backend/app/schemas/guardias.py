from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class GuardiaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asignacion_id: UUID
    dictado_id: UUID
    dia: str = Field(..., pattern=r"^(Lunes|Martes|Miércoles|Jueves|Viernes|Sábado|Domingo)$")
    horario: str = Field(..., min_length=1, max_length=50)
    comentarios: str | None = None


class GuardiaRead(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    asignacion_id: UUID
    dictado_id: UUID
    dia: str
    horario: str
    estado: str
    comentarios: str | None = None
    creada_at: datetime


class GuardiaUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    estado: str | None = Field(
        None, pattern=r"^(Pendiente|Realizada|Cancelada)$"
    )
    comentarios: str | None = None


class GuardiaExportRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dia: str
    horario: str
    materia: str
    docente: str
    estado: str
    comentarios: str | None = None
