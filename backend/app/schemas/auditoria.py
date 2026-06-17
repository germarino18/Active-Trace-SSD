"""Pydantic schemas for auditoria (audit panel and metrics) module."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ── Filtros compartidos ──────────────────────────────────────────────


class AuditoriaFiltros(BaseModel):
    """Shared query parameters for audit log filtering."""
    model_config = ConfigDict(extra="forbid")

    fecha_desde: datetime | None = None
    fecha_hasta: datetime | None = None
    materia_id: UUID | None = None
    usuario_id: UUID | None = None


# ── Acciones por día ─────────────────────────────────────────────────


class AccionesPorDiaItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fecha: str  # ISO date string
    total: int = Field(..., ge=0)


# ── Comunicaciones por docente ───────────────────────────────────────


class ComunicacionesPorDocenteItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    docente_id: UUID
    materia_id: UUID
    pendiente: int = Field(0, ge=0)
    enviando: int = Field(0, ge=0)
    enviado: int = Field(0, ge=0)
    error: int = Field(0, ge=0)
    cancelado: int = Field(0, ge=0)


# ── Interacciones por docente y materia ──────────────────────────────


class InteraccionItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accion: str
    total: int = Field(..., ge=0)


class InteraccionesPorDocenteMateriaItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    docente_id: UUID
    materia_id: UUID
    interacciones: list[InteraccionItem]


# ── Últimas acciones (log detallado) ─────────────────────────────────


class UltimasAccionesItem(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    fecha_hora: datetime
    actor_id: UUID
    actor_nombre: str | None = None
    impersonado_id: UUID | None = None
    materia_id: UUID | None = None
    materia_nombre: str | None = None
    accion: str
    detalle: dict | None = None
    filas_afectadas: int | None = None
    ip: str | None = None
    user_agent: str | None = None


class UltimasAccionesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[UltimasAccionesItem]
    limit: int


# ── Log completo de auditoría (paginado) ─────────────────────────────


class LogAuditoriaItem(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    fecha_hora: datetime
    actor_id: UUID
    actor_nombre: str | None = None
    impersonado_id: UUID | None = None
    materia_id: UUID | None = None
    materia_nombre: str | None = None
    accion: str
    detalle: dict | None = None
    filas_afectadas: int | None = None
    ip: str | None = None
    user_agent: str | None = None


class LogAuditoriaPaginado(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[LogAuditoriaItem]
    total: int = Field(..., ge=0)
    offset: int = Field(..., ge=0)
    limit: int = Field(..., ge=1, le=200)
