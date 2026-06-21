"""Pydantic schemas for Actividad (C-25)."""

import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class ActividadCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str = Field(..., min_length=1, max_length=255)
    tipo: str = Field(..., min_length=1, max_length=50)
    fecha_limite: date | None = None


class ActividadUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str | None = Field(None, min_length=1, max_length=255)
    tipo: str | None = Field(None, min_length=1, max_length=50)
    fecha_limite: date | None = None


class ActividadResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    dictado_id: uuid.UUID
    nombre: str
    tipo: str
    fecha_limite: date | None
