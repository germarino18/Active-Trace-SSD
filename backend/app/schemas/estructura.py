from datetime import date
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EstadoCarreraMateria(str, Enum):
    """Estado de Carrera, Materia y Cohorte (D7)."""

    ACTIVA = "Activa"
    INACTIVA = "Inactiva"


class EstadoDictado(str, Enum):
    """Estado de Dictado (D7 — género distinto al de Carrera/Materia/Cohorte)."""

    ACTIVO = "Activo"
    INACTIVO = "Inactivo"


# ── Carrera ──────────────────────────────────────────────────────────────


class CarreraCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    codigo: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=255)


class CarreraUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    codigo: str | None = Field(default=None, max_length=50)
    nombre: str | None = Field(default=None, max_length=255)
    estado: EstadoCarreraMateria | None = None


class CarreraResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID
    tenant_id: UUID
    codigo: str
    nombre: str
    estado: EstadoCarreraMateria
    deleted_at: bool = False


# ── Materia ──────────────────────────────────────────────────────────────


class MateriaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    codigo: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=255)


class MateriaUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    codigo: str | None = Field(default=None, max_length=50)
    nombre: str | None = Field(default=None, max_length=255)
    estado: EstadoCarreraMateria | None = None


class MateriaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID
    tenant_id: UUID
    codigo: str
    nombre: str
    estado: EstadoCarreraMateria
    deleted_at: bool = False


# ── Cohorte ──────────────────────────────────────────────────────────────


class CohorteCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    carrera_id: UUID
    nombre: str = Field(..., max_length=100)
    anio: int | None = None
    vig_desde: date | None = None
    vig_hasta: date | None = None


class CohorteUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nombre: str | None = Field(default=None, max_length=100)
    anio: int | None = None
    vig_desde: date | None = None
    vig_hasta: date | None = None
    estado: EstadoCarreraMateria | None = None


class CohorteResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID
    tenant_id: UUID
    carrera_id: UUID
    nombre: str
    anio: int | None = None
    vig_desde: date | None = None
    vig_hasta: date | None = None
    estado: EstadoCarreraMateria
    deleted_at: bool = False


# ── Dictado ──────────────────────────────────────────────────────────────


class DictadoCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    materia_id: UUID
    carrera_id: UUID
    cohorte_id: UUID


class DictadoUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    estado: EstadoDictado | None = None


class DictadoResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID
    tenant_id: UUID
    materia_id: UUID
    carrera_id: UUID
    cohorte_id: UUID
    estado: EstadoDictado
    deleted_at: bool = False
