"""DTOs para operaciones de equipo docente (C-08), sobre `Asignacion` (E5).

Un "equipo" es el conjunto de asignaciones que comparten la tripleta de
contexto `(materia_id, carrera_id, cohorte_id)` dentro de un tenant (D2) —
no es una entidad propia, no hay tabla nueva. Todos los esquemas usan
`model_config = ConfigDict(extra='forbid')` (regla dura #5). `estado_vigencia`
es siempre DERIVADO por fechas (D3, reusa `estado_vigencia_for()`), nunca
aceptado en un request ni almacenado.
"""

import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.asignacion import EstadoVigencia, RolAsignacion


class AsignacionMasivaCreate(BaseModel):
    """Asignar un bloque de N docentes a materia x carrera x cohorte x rol
    con una vigencia común (F4.4, RN-30).

    Todos los `usuario_id` y el contexto académico se validan contra el
    tenant de la sesión (D4) -- una referencia ajena es indistinguible de
    "no existe" (404, regla dura #9).
    """

    model_config = ConfigDict(extra="forbid")
    usuario_ids: list[UUID] = Field(..., min_length=1)
    materia_id: UUID
    carrera_id: UUID
    cohorte_id: UUID
    rol: RolAsignacion
    desde: datetime.date
    hasta: datetime.date | None = None


class ClonarEquipoCreate(BaseModel):
    """Clonar las asignaciones VIGENTES de un equipo origen hacia un destino
    con la misma materia/carrera y una nueva cohorte (F4.5, RN-12, D5)."""

    model_config = ConfigDict(extra="forbid")
    materia_id: UUID
    carrera_id: UUID
    cohorte_origen_id: UUID
    cohorte_destino_id: UUID
    desde: datetime.date
    hasta: datetime.date | None = None


class VigenciaEquipoUpdate(BaseModel):
    """Actualizar `desde`/`hasta` de todas las asignaciones vivas de un
    equipo (materia x carrera x cohorte) en bloque (F4.6).

    `desde` y `hasta` son opcionales: sólo se actualizan los campos provistos.
    """

    model_config = ConfigDict(extra="forbid")
    materia_id: UUID
    carrera_id: UUID
    cohorte_id: UUID
    desde: datetime.date | None = None
    hasta: datetime.date | None = None


class MisEquiposFiltros(BaseModel):
    """Filtros opcionales para `GET /api/equipos/mis-equipos` (F4.2).

    `usuario_id`/`tenant_id` NUNCA viajan acá: se derivan de la sesión
    (D3 [SEC], regla dura #8).
    """

    model_config = ConfigDict(extra="forbid")
    estado: EstadoVigencia | None = None
    materia_id: UUID | None = None
    rol: RolAsignacion | None = None
    carrera_id: UUID | None = None
    cohorte_id: UUID | None = None


class EquipoFiltros(BaseModel):
    """Filtros opcionales para `GET /api/equipos` (F4.3, listado del tenant)."""

    model_config = ConfigDict(extra="forbid")
    materia_id: UUID | None = None
    carrera_id: UUID | None = None
    cohorte_id: UUID | None = None
    usuario_id: UUID | None = None
    rol: RolAsignacion | None = None
    responsable_id: UUID | None = None


class EquipoExportItem(BaseModel):
    """Una fila del export CSV de un equipo (F4.7, D8).

    `estado_vigencia` es DERIVADO por fechas (D3), nunca almacenado.
    """

    model_config = ConfigDict(extra="forbid")
    usuario_id: UUID
    docente: str
    rol: RolAsignacion
    materia_id: UUID | None = None
    carrera_id: UUID | None = None
    cohorte_id: UUID | None = None
    desde: datetime.date
    hasta: datetime.date | None = None
    estado_vigencia: EstadoVigencia


class EquipoAsignacionResponse(BaseModel):
    """Una fila de respuesta para "mis-equipos" (F4.2) y el listado del
    tenant (F4.3): una `Asignacion` con `estado_vigencia` DERIVADO por
    fechas (D3, nunca almacenado). A diferencia de `AsignacionResponse`
    (C-07), no expone `tenant_id`/`deleted_at` — ambos endpoints sólo
    devuelven filas vivas del tenant de la sesión."""

    model_config = ConfigDict(extra="forbid")
    id: UUID
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


class AsignacionMasivaResultado(BaseModel):
    """Resultado de una operación de bloque (masiva o clonado): ids creados
    vs. ya-existentes omitidos (D5, "omitir y reportar") y filas afectadas
    para el evento `ASIGNACION_MODIFICAR` (D6/D7)."""

    model_config = ConfigDict(extra="forbid")
    creadas: list[UUID] = Field(default_factory=list)
    ya_existentes: list[UUID] = Field(default_factory=list)
    filas_afectadas: int


class DocenteResponse(BaseModel):
    """Una fila de respuesta del autocompletado de docentes (F4.4, RN-30,
    `GET /api/equipos/docentes`)."""

    model_config = ConfigDict(extra="forbid")
    usuario_id: UUID
    nombre: str
    apellidos: str
