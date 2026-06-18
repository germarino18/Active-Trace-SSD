"""Pydantic schemas for analytics module."""

from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class AtrasadosPorCohorteItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    fecha: str  # ISO date string YYYY-MM-DD
    cohorte: str
    total_atrasados: int = Field(..., ge=0)
    total_alumnos: int = Field(..., ge=0)
    porcentaje: float = Field(..., ge=0.0, le=100.0)


class DistribucionNotasItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rango: str  # "0-25%", "26-50%", etc.
    cantidad: int = Field(..., ge=0)


class PrediccionAbandonoItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    alumno_id: UUID
    alumno_nombre: str
    materia: str
    promedio: float = Field(..., ge=0.0)
    atrasos: int = Field(..., ge=0)
    riesgo: str  # "bajo" | "medio" | "alto"


class DashboardResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    total_alumnos: int = Field(..., ge=0)
    total_atrasados_actual: int = Field(..., ge=0)
    promedio_general: float = Field(..., ge=0.0)
    alumnos_en_riesgo: dict[str, int]  # {"bajo": N, "medio": N, "alto": N}
    tendencia_atrasados_ultimo_mes: list[dict]  # [{fecha, total}]
    total_materias: int = Field(..., ge=0)
