"""Pydantic schemas for tareas (internal task management)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import inspect as sa_inspect

from app.models.tarea import TareaEstado


class TareaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asignado_a: UUID
    materia_id: UUID | None = None
    descripcion: str = Field(..., min_length=1)
    contexto_id: UUID | None = None


class TareaCreatePropia(BaseModel):
    """Crear una tarea auto-asignada (el autor es también el destinatario)."""

    model_config = ConfigDict(extra="forbid")

    materia_id: UUID | None = None
    descripcion: str = Field(..., min_length=1)


class TareaUpdateEstado(BaseModel):
    model_config = ConfigDict(extra="forbid")

    estado: TareaEstado
    comentario: str | None = None


class ComentarioCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    texto: str = Field(..., min_length=1)


class ComentarioRead(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    tarea_id: UUID
    autor_id: UUID
    texto: str
    creado_at: datetime


class TareaRead(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    tenant_id: UUID
    materia_id: UUID | None = None
    asignado_a: UUID
    asignado_por: UUID
    estado: str
    descripcion: str
    contexto_id: UUID | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    comentarios: list[ComentarioRead] = []

    @model_validator(mode="before")
    @classmethod
    def _skip_lazy_relations(cls, data):
        if not hasattr(data, "_sa_instance_state"):
            return data
        state = sa_inspect(data)
        unloaded = state.unloaded
        return {
            attr: getattr(data, attr)
            for attr in cls.model_fields
            if attr not in unloaded
        }


class TareaFilterParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    estado: str | None = None
    materia_id: UUID | None = None
    texto: str | None = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=200)
