from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ComunicacionPreviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    destinatario_nombre: str = Field(..., description="Nombre del alumno para sustituir en template")
    destinatario_apellido: str = Field(..., description="Apellido del alumno para sustituir en template")
    materia_nombre: str = Field(..., description="Nombre de la materia para sustituir en template")
    docente_nombre: str = Field(..., description="Nombre del docente para sustituir en template")
    asunto_template: str = Field(..., min_length=1, description="Asunto con variables $alumno_nombre, etc.")
    cuerpo_template: str = Field(..., min_length=1, description="Cuerpo con variables $alumno_nombre, etc.")


class ComunicacionPreview(BaseModel):
    model_config = ConfigDict(extra="forbid")
    asunto: str
    cuerpo: str


class EnvioMasivoItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    usuario_id: UUID
    destinatario_email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    destinatario_nombre: str
    destinatario_apellido: str


class EnvioMasivoRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    materia_id: UUID
    asunto_template: str = Field(..., min_length=1)
    cuerpo_template: str = Field(..., min_length=1)
    destinatarios: list[EnvioMasivoItem] = Field(..., min_length=1)


class EnvioMasivoResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    lote_id: UUID
    total: int


class ComunicacionRead(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)
    id: UUID
    enviado_por: UUID
    materia_id: UUID
    destinatario: str
    asunto: str
    estado: str
    lote_id: UUID
    enviado_at: datetime | None = None
    reintentos: int


class LoteResumen(BaseModel):
    model_config = ConfigDict(extra="forbid")
    lote_id: UUID
    total: int
    pendientes: int
    enviados: int
    errores: int
    cancelados: int


class LoteComunicacionItem(BaseModel):
    """A pending communication lot as shown in the approval list."""

    model_config = ConfigDict(extra="forbid")
    lote_id: UUID
    docente_id: UUID
    docente_nombre: str
    asunto: str
    cuerpo: str
    total_destinatarios: int
    created_at: datetime


class LotesPendientesResponse(BaseModel):
    """Paginated response for pending approval lots."""

    model_config = ConfigDict(extra="forbid")
    items: list[LoteComunicacionItem]
    total: int


class ComunicacionEstadoUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    estado: str = Field(..., pattern=r"^(Enviando|Cancelado)$")
