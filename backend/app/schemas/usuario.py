from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EstadoUsuario(str, Enum):
    """Estado de Usuario (E4)."""

    ACTIVO = "Activo"
    INACTIVO = "Inactivo"


class UsuarioCreate(BaseModel):
    """Crear el perfil de negocio `Usuario` (E4), 1:1 con `users` (D1).

    `user_id` debe apuntar a una identidad `users` existente del mismo
    tenant (regla dura #9, validado por el servicio). `email` NO se acepta
    acá: vive solo en `users.email` (D1).
    """

    model_config = ConfigDict(extra="forbid")
    user_id: UUID
    nombre: str = Field(..., max_length=255)
    apellidos: str = Field(..., max_length=255)
    dni: str | None = None
    cuil: str | None = None
    cbu: str | None = None
    alias_cbu: str | None = None
    banco: str | None = Field(default=None, max_length=255)
    regional: str | None = Field(default=None, max_length=100)
    legajo: str | None = Field(default=None, max_length=50)
    legajo_profesional: str | None = Field(default=None, max_length=50)
    facturador: bool = False


class UsuarioUpdate(BaseModel):
    """Actualizar el perfil `Usuario`. Todos los campos son opcionales.

    `user_id` NO es actualizable: el vínculo 1:1 con `users` es fijo desde
    la creación (regla dura #14 — identidad nunca se reasigna vía ABM).
    """

    model_config = ConfigDict(extra="forbid")
    nombre: str | None = Field(default=None, max_length=255)
    apellidos: str | None = Field(default=None, max_length=255)
    dni: str | None = None
    cuil: str | None = None
    cbu: str | None = None
    alias_cbu: str | None = None
    banco: str | None = Field(default=None, max_length=255)
    regional: str | None = Field(default=None, max_length=100)
    legajo: str | None = Field(default=None, max_length=50)
    legajo_profesional: str | None = Field(default=None, max_length=50)
    facturador: bool | None = None
    estado: EstadoUsuario | None = None


class UsuarioResponse(BaseModel):
    """Respuesta por defecto: NUNCA incluye PII cifrada (`dni`/`cuil`/`cbu`/
    `alias_cbu`) — regla dura #12 y spec `usuarios` Scenario "PII is not
    exposed in default responses"."""

    model_config = ConfigDict(extra="forbid")
    id: UUID
    tenant_id: UUID
    user_id: UUID
    nombre: str
    apellidos: str
    banco: str | None = None
    regional: str | None = None
    legajo: str | None = None
    legajo_profesional: str | None = None
    facturador: bool
    estado: EstadoUsuario
    deleted_at: bool = False
