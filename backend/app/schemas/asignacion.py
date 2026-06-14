import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RolAsignacion(str, Enum):
    """Roles aceptados por `Asignacion.rol` (D3) — los 7 códigos sembrados en C-04."""

    ALUMNO = "ALUMNO"
    PROFESOR = "PROFESOR"
    TUTOR = "TUTOR"
    COORDINADOR = "COORDINADOR"
    NEXO = "NEXO"
    ADMIN = "ADMIN"
    FINANZAS = "FINANZAS"


class EstadoVigencia(str, Enum):
    """Estado de vigencia derivado por fechas (D3), NUNCA almacenado."""

    VIGENTE = "Vigente"
    VENCIDA = "Vencida"


class AsignacionCreate(BaseModel):
    """Crear una `Asignacion` (E5): Usuario <-> Rol <-> contexto académico.

    Contexto (`dictado_id`/`materia_id`/`carrera_id`/`cohorte_id`) es
    nullable; todos NULL = rol tenant-global (D3). `estado_vigencia` NO se
    acepta acá: es derivado, nunca almacenado.
    """

    model_config = ConfigDict(extra="forbid")
    usuario_id: UUID
    rol: RolAsignacion
    dictado_id: UUID | None = None
    materia_id: UUID | None = None
    carrera_id: UUID | None = None
    cohorte_id: UUID | None = None
    comisiones: list[str] = Field(default_factory=list)
    responsable_id: UUID | None = None
    desde: datetime.date
    hasta: datetime.date | None = None


class AsignacionUpdate(BaseModel):
    """Actualizar una `Asignacion`. Todos los campos son opcionales.

    `usuario_id` NO es actualizable: el vínculo a un perfil `Usuario` es
    fijo desde la creación.
    """

    model_config = ConfigDict(extra="forbid")
    rol: RolAsignacion | None = None
    dictado_id: UUID | None = None
    materia_id: UUID | None = None
    carrera_id: UUID | None = None
    cohorte_id: UUID | None = None
    comisiones: list[str] | None = None
    responsable_id: UUID | None = None
    desde: datetime.date | None = None
    hasta: datetime.date | None = None


class AsignacionResponse(BaseModel):
    """Respuesta: incluye `estado_vigencia` DERIVADO por fechas (D3, nunca
    una columna almacenada) — spec `asignaciones` "estado_vigencia is
    derived, not stored"."""

    model_config = ConfigDict(extra="forbid")
    id: UUID
    tenant_id: UUID
    usuario_id: UUID
    rol: RolAsignacion
    dictado_id: UUID | None = None
    materia_id: UUID | None = None
    carrera_id: UUID | None = None
    cohorte_id: UUID | None = None
    comisiones: list[str]
    responsable_id: UUID | None = None
    desde: datetime.date
    hasta: datetime.date | None = None
    estado_vigencia: EstadoVigencia
    deleted_at: bool = False
