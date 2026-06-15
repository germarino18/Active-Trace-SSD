"""DTOs para operaciones de padrón (C-09): importación/previsualización,
consulta de versión activa, historial de versiones y vaciado.

Todos los esquemas usan `model_config = ConfigDict(extra='forbid')`
(regla dura #5). `VersionPadronResponse`/`EntradaPadronResponse` son
`from_attributes=True` para mapear desde modelos ORM.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class VersionPadronResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    dictado_id: UUID
    cargado_por: UUID
    cargado_at: datetime
    activa: bool


class EntradaPadronResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    version_id: UUID
    usuario_id: UUID | None = None
    nombre: str
    apellidos: str
    email: str | None = None
    comision: str | None = None
    regional: str | None = None


class PadronPreviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dictado_id: UUID


class PadronPreviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    columnas_encontradas: list[str]
    filas: list[dict]
    total_filas: int
    preview_token: str


class PadronImportConfirm(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dictado_id: UUID
    preview_token: str


class PadronImportResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version_id: UUID
    total_importados: int
    mensaje: str


class PadronVaciarResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dictado_id: UUID
    entradas_eliminadas: int
    mensaje: str


class VersionPadronHistoryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    versiones: list[VersionPadronResponse]
