from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EvaluacionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dictado_id: UUID
    tipo: str = Field(
        ..., pattern=r"^(Parcial|TP|Coloquio|Recuperatorio)$"
    )
    instancia: str = Field(..., min_length=1, max_length=255)
    dias_disponibles: int = Field(default=10, ge=1, le=365)
    cupo_maximo: int = Field(..., ge=1)


class EvaluacionRead(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    dictado_id: UUID
    tipo: str
    instancia: str
    dias_disponibles: int
    cupo_maximo: int
    estado: str
    created_at: datetime
    updated_at: datetime


class EvaluacionUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dias_disponibles: int | None = Field(None, ge=1, le=365)
    cupo_maximo: int | None = Field(None, ge=1)
    instancia: str | None = Field(None, min_length=1, max_length=255)


class ReservaEvaluacionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evaluacion_id: UUID


class ReservaEvaluacionRead(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    evaluacion_id: UUID
    alumno_id: UUID
    fecha_hora: datetime
    estado: str


class ResultadoEvaluacionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evaluacion_id: UUID
    alumno_id: UUID
    nota_final: str = Field(..., min_length=1, max_length=255)


class ResultadoEvaluacionRead(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    evaluacion_id: UUID
    alumno_id: UUID
    nota_final: str


class AlumnoConvocadoCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alumno_ids: list[UUID]


class AlumnoConvocadoRead(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    evaluacion_id: UUID
    alumno_id: UUID


class MetricasColoquiosRead(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_alumnos_convocados: int
    instancias_activas: int
    reservas_activas: int
    notas_registradas: int


class AgendaReservaRead(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    evaluacion_id: UUID
    alumno_id: UUID
    alumno_nombre: str
    alumno_legajo: str | None
    evaluacion_instancia: str
    dictado_id: UUID
    materia_nombre: str
    fecha_hora: datetime
    estado: str


class RegistroAcademicoRead(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alumno_id: UUID
    alumno_nombre: str
    alumno_legajo: str | None
    evaluacion_id: UUID
    evaluacion_instancia: str
    dictado_id: UUID
    materia_nombre: str
    tipo: str
    nota_final: str
    fecha_reserva: datetime | None
