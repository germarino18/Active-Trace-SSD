from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AtrasadosQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")
    dictado_id: UUID


class RankingQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")
    dictado_id: UUID


class ReporteQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")


class MonitorGeneralQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")
    materia_id: UUID | None = None
    dictado_id: UUID | None = None
    comision: str | None = None
    q: str | None = None
    estado: str | None = Field(default=None, pattern=r"^(aprobado|desaprobado|atrasado)$")
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=200)


class MonitorSeguimientoQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")
    materia_id: UUID | None = None
    dictado_id: UUID | None = None
    comision: str | None = None
    q: str | None = None
    minimo_cumplidas: int | None = Field(default=None, ge=1)
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=200)
    desde: date | None = None
    hasta: date | None = None

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.desde is not None and self.hasta is not None and self.desde > self.hasta:
            raise ValueError("desde must be <= hasta")
        return self


class AlumnoAtrasado(BaseModel):
    model_config = ConfigDict(extra="forbid")
    alumno_id: UUID
    alumno_nombre: str
    alumno_apellido: str
    comision: str | None = None
    actividades_faltantes: list[str] = Field(default_factory=list)
    actividades_desaprobadas: list[str] = Field(default_factory=list)


class RankingItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    alumno_id: UUID
    alumno_nombre: str
    alumno_apellido: str
    aprobadas: int
    total_actividades: int


class ReporteMateria(BaseModel):
    model_config = ConfigDict(extra="forbid")
    total_alumnos: int
    aprobados: int
    atrasados: int
    total_actividades: int
    promedio_general: float | None = None
    sin_datos: bool = False


class NotaFinalAlumno(BaseModel):
    model_config = ConfigDict(extra="forbid")
    alumno_id: UUID
    alumno_nombre: str
    alumno_apellido: str
    nota_final: float | None = None
    actividades_consideradas: int = 0


class TPSinCorregir(BaseModel):
    model_config = ConfigDict(extra="forbid")
    alumno_id: UUID
    alumno_nombre: str
    alumno_apellido: str
    actividad: str
    fecha_finalizacion: str | None = None
    dictado_id: UUID
    comision: str | None = None


class MonitorItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    alumno_id: UUID
    alumno_nombre: str
    alumno_apellido: str
    comision: str | None = None
    actividades_totales: int
    actividades_aprobadas: int
    actividades_desaprobadas: int
    actividades_faltantes: int
    estado: str


class MonitorPaginado(BaseModel):
    model_config = ConfigDict(extra="forbid")
    items: list[MonitorItem]
    total_count: int
    offset: int
    limit: int
