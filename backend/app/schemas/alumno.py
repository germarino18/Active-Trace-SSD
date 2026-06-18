"""Pydantic schemas for the alumno (student) module."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ── Dashboard ───────────────────────────────────────────────────────

class MateriaDashboardItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    nombre: str
    profesor: str
    progreso: dict
    estado: str


class ProximoColoquioItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    materia_nombre: str
    fecha: str
    cupos_restantes: int


class ProximaFechaItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    materia_nombre: str
    tipo: str
    fecha: str
    descripcion: str


class AlumnoDashboardResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materias: list[MateriaDashboardItem]
    avisos_no_leidos: int
    comunicaciones_no_leidas: int
    proximos_coloquios: list[ProximoColoquioItem]
    proximas_fechas: list[ProximaFechaItem]


# ── Estado académico ────────────────────────────────────────────────

class ActividadEstado(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    nombre: str
    nota: float | None = None
    estado: str


class EstadoAcademicoMateria(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    nombre: str
    profesor: str
    actividades: list[ActividadEstado]
    promedio: float | None = None
    condicion: str


# ── Programas ───────────────────────────────────────────────────────

class ProgramaMateriaRead(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    materia_nombre: str
    programa_nombre: str
    fecha_publicacion: str
    referencia_archivo: str | None = None


# ── Comunicaciones recibidas ────────────────────────────────────────

class ComunicacionRecibidaRead(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    remitente: str
    materia_nombre: str
    asunto: str
    fecha_envio: str
    estado: str


class ComunicacionDetalleRead(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    asunto: str
    cuerpo: str
    remitente: str
    materia_nombre: str
    fecha_envio: str
    estado_entrega: str
