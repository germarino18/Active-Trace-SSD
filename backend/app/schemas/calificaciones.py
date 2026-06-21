from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CalificacionEditRequest(BaseModel):
    """Schema para edición individual de calificación (C-25 §5)."""
    model_config = ConfigDict(extra="forbid")

    nota_numerica: Decimal | None = None
    nota_textual: str | None = None
    aprobado: bool | None = None


class CalificacionResponse(BaseModel):
    model_config = ConfigDict(extra='forbid', from_attributes=True)
    id: UUID
    entrada_padron_id: UUID
    dictado_id: UUID
    actividad: str
    nota_numerica: Decimal | None = None
    nota_textual: str | None = None
    aprobado: bool
    origen: str
    importado_at: datetime


class CalificacionImportRow(BaseModel):
    model_config = ConfigDict(extra='forbid')
    entrada_padron_id: UUID | None = None
    actividad: str
    nota_numerica: Decimal | None = None
    nota_textual: str | None = None


class ActividadDetectada(BaseModel):
    model_config = ConfigDict(extra='forbid')
    nombre: str
    tipo: str
    tiene_nota: bool


class PreviewCalificacionesResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')
    actividades_detectadas: list[ActividadDetectada]
    filas: list[dict]
    total_filas: int
    preview_token: str


class PreviewCalificacionesRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    dictado_id: UUID


class ImportCalificacionesConfirm(BaseModel):
    model_config = ConfigDict(extra='forbid')
    dictado_id: UUID
    preview_token: str
    actividades_seleccionadas: list[str]


class ImportCalificacionesResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')
    total_importados: int
    aprobados: int
    desaprobados: int
    mensaje: str


class UmbralMateriaCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    dictado_id: UUID
    umbral_pct: int = Field(default=60, ge=0, le=100)
    valores_aprobatorios: list[str] | None = None


class UmbralMateriaUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    umbral_pct: int | None = Field(default=None, ge=0, le=100)
    valores_aprobatorios: list[str] | None = None


class UmbralMateriaResponse(BaseModel):
    model_config = ConfigDict(extra='forbid', from_attributes=True)
    id: UUID
    asignacion_id: UUID
    dictado_id: UUID
    umbral_pct: int
    valores_aprobatorios: list[str] | None = None
