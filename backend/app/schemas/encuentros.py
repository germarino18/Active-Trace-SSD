from datetime import date, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SlotEncuentroCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dictado_id: UUID
    asignacion_id: UUID | None = None
    titulo: str = Field(..., min_length=1, max_length=255)
    hora: time
    dia_semana: str = Field(..., pattern=r"^(Lunes|Martes|Miércoles|Jueves|Viernes|Sábado|Domingo)$")
    fecha_inicio: date
    cant_semanas: int = Field(default=0, ge=0, le=52)
    fecha_unica: date | None = None
    meet_url: str | None = Field(None, max_length=500)
    vig_desde: date
    vig_hasta: date | None = None


class SlotEncuentroRead(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    dictado_id: UUID
    asignacion_id: UUID | None = None
    titulo: str
    hora: time
    dia_semana: str
    fecha_inicio: date
    cant_semanas: int
    fecha_unica: date | None = None
    meet_url: str | None = None
    vig_desde: date
    vig_hasta: date | None = None


class SlotEncuentroUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    titulo: str | None = Field(None, min_length=1, max_length=255)
    hora: time | None = None
    dia_semana: str | None = Field(
        None, pattern=r"^(Lunes|Martes|Miércoles|Jueves|Viernes|Sábado|Domingo)$"
    )
    meet_url: str | None = Field(None, max_length=500)
    vig_desde: date | None = None
    vig_hasta: date | None = None


class InstanciaEncuentroCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dictado_id: UUID
    asignacion_id: UUID | None = None
    fecha: date
    hora: time
    titulo: str = Field(..., min_length=1, max_length=255)
    meet_url: str | None = Field(None, max_length=500)


class InstanciaEncuentroRead(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    slot_id: UUID | None = None
    dictado_id: UUID
    asignacion_id: UUID | None = None
    fecha: date
    hora: time
    titulo: str
    estado: str
    meet_url: str | None = None
    video_url: str | None = None
    comentario: str | None = None


class InstanciaEncuentroUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    estado: str | None = Field(
        None, pattern=r"^(Programado|Realizado|Cancelado)$"
    )
    meet_url: str | None = Field(None, max_length=500)
    video_url: str | None = Field(None, max_length=500)
    comentario: str | None = None


class BloqueHTMLResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    html: str
    dictado_id: UUID
    total_encuentros: int
