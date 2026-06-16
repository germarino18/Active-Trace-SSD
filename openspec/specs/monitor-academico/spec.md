## ADDED Requirements

### Requirement: Monitor de seguimiento de alumnos — vista TUTOR/PROFESOR (F2.8)

El sistema SHALL proveer una vista filtrable del estado de actividades de los alumnos asignados al TUTOR o PROFESOR. Los filtros disponibles son: alumno, correo, comisión, regional, actividad, mínimo de actividad cumplida. El alcance SHALL estar limitado a los dictados donde el usuario tiene asignaciones vigentes. El endpoint SHALL estar gated por `atrasados:ver`.

#### Scenario: Consulta de seguimiento para TUTOR
- **WHEN** un TUTOR consulta `GET /api/v1/analisis/monitor/seguimiento`
- **THEN** el sistema devuelve alumnos de sus asignaciones vigentes con estado de actividades

#### Scenario: Consulta filtrada por comisión
- **WHEN** un PROFESOR consulta con `comision_id=X`
- **THEN** el sistema devuelve solo alumnos de esa comisión dentro de sus asignaciones

#### Scenario: Filtro por mínimo de actividades cumplidas
- **WHEN** un TUTOR consulta con `minimo_cumplidas=3`
- **THEN** el sistema devuelve solo alumnos con al menos 3 actividades aprobadas

#### Scenario: TUTOR sin asignaciones
- **WHEN** un TUTOR sin asignaciones vigentes consulta el monitor
- **THEN** el sistema devuelve lista vacía

### Requirement: Monitor de seguimiento extendido — vista COORDINADOR/ADMIN (F2.9)

El sistema SHALL extender la vista de seguimiento (F2.8) para COORDINADOR y ADMIN con un filtro adicional de rango de fechas. Estos roles NO están limitados por asignaciones vigentes y pueden ver cualquier dictado del tenant. El endpoint SHALL estar gated por `atrasados:ver`.

#### Scenario: Consulta con rango de fechas
- **WHEN** un COORDINADOR consulta con `desde=2026-01-01&hasta=2026-06-30`
- **THEN** el sistema filtra actividades dentro del rango de fechas especificado

#### Scenario: Consulta sin rango de fechas
- **WHEN** un ADMIN consulta sin parámetros de fecha
- **THEN** el sistema devuelve todas las actividades sin filtro temporal

#### Scenario: Acceso a cualquier dictado del tenant
- **WHEN** un COORDINADOR consulta por un dictado sin asignación personal
- **THEN** el sistema permite la consulta (alcance tenant completo)

#### Scenario: Rango de fechas inválido
- **WHEN** un usuario envía `desde` posterior a `hasta`
- **THEN** el sistema responde 422 con error de validación

### Requirement: Paginación estándar en monitores

Todos los endpoints de monitor SHALL soportar paginación mediante parámetros `offset` (default 0) y `limit` (default 50, máximo 200).

#### Scenario: Paginación con offset y limit
- **WHEN** un usuario consulta con `offset=50&limit=25`
- **THEN** el sistema devuelve los resultados de la página 3 (ítems 51-75) e incluye `total_count` en la respuesta

#### Scenario: Limit excede máximo
- **WHEN** un usuario consulta con `limit=500`
- **THEN** el sistema trunca a `limit=200` sin error
