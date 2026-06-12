from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ── Rol ─────────────────────────────────────────────────────────────────
class RolCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    codigo: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=100)
    descripcion: str | None = None


class RolUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    codigo: str | None = Field(default=None, max_length=50)
    nombre: str | None = Field(default=None, max_length=100)
    descripcion: str | None = None


class RolResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID
    tenant_id: UUID
    codigo: str
    nombre: str
    descripcion: str | None = None
    deleted_at: bool = False


# ── Permiso ─────────────────────────────────────────────────────────────
class PermisoCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    codigo: str = Field(..., max_length=100)
    nombre: str = Field(..., max_length=255)
    descripcion: str | None = None
    modulo: str = Field(..., max_length=50)


class PermisoUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    codigo: str | None = Field(default=None, max_length=100)
    nombre: str | None = Field(default=None, max_length=255)
    descripcion: str | None = None
    modulo: str | None = Field(default=None, max_length=50)


class PermisoResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID
    tenant_id: UUID
    codigo: str
    nombre: str
    descripcion: str | None = None
    modulo: str
    deleted_at: bool = False


# ── RolPermiso ──────────────────────────────────────────────────────────
class RolPermisoCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    permiso_id: UUID


class PermisoInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    permiso_codigo: str
    es_propio: bool
