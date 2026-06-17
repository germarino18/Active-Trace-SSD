from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class HiloResponse(BaseModel):
    """Resumen de un hilo de conversación para la lista del inbox."""

    model_config = ConfigDict(extra="forbid")

    id: UUID
    remitente_id: UUID
    remitente_nombre: str
    asunto: str
    ultimo_mensaje: str
    ultima_fecha: datetime
    no_leido: bool


class MensajeResponse(BaseModel):
    """Mensaje individual dentro de un hilo."""

    model_config = ConfigDict(extra="forbid")

    id: UUID
    remitente_id: UUID
    remitente_nombre: str
    contenido: str
    fecha_hora: datetime


class ResponderRequest(BaseModel):
    """Cuerpo para responder en un hilo existente."""

    model_config = ConfigDict(extra="forbid")

    contenido: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Contenido del mensaje (1-2000 caracteres)",
    )
