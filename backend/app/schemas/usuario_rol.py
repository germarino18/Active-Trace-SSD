from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UsuarioRolCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rol_id: UUID
    desde: date | None = None
    hasta: date | None = None


class UsuarioRolResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID
    usuario_id: UUID
    rol_id: UUID
    rol_nombre: str | None = None
    desde: date | None = None
    hasta: date | None = None
    created_at: datetime | None = None
