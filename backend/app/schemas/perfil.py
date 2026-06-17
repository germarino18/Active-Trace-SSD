from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PerfilResponse(BaseModel):
    """Respuesta del perfil propio del usuario autenticado.

    Incluye PII descifrada (dni, cuil, cbu, alias_cbu) porque el dueño
    del perfil tiene derecho a ver sus propios datos. El email se obtiene
    desde la tabla `users` (no se duplica en `usuario`).
    """

    model_config = ConfigDict(extra="forbid")

    id: UUID
    user_id: UUID
    nombre: str
    apellidos: str
    email: str
    dni: str | None = None
    cuil: str | None = None
    cbu: str | None = None
    alias_cbu: str | None = None
    banco: str | None = None
    regional: str | None = None
    legajo: str | None = None
    legajo_profesional: str | None = None
    facturador: bool
    estado: str


class PerfilUpdate(BaseModel):
    """Actualización parcial del perfil propio.

    Solo se permiten campos editables. `cuil` NO está incluido
    intencionalmente — es solo lectura (spec `perfil-propio` Scenario:
    "PATCH with CUIL returns 422"). Si se incluye, `extra='forbid'` lo
    rechaza automáticamente.
    """

    model_config = ConfigDict(extra="forbid")

    nombre: str | None = Field(default=None, max_length=255)
    apellidos: str | None = Field(default=None, max_length=255)
    dni: str | None = None
    cbu: str | None = None
    alias_cbu: str | None = None
    banco: str | None = Field(default=None, max_length=255)
    regional: str | None = Field(default=None, max_length=100)
    legajo_profesional: str | None = Field(default=None, max_length=50)
    facturador: bool | None = None
