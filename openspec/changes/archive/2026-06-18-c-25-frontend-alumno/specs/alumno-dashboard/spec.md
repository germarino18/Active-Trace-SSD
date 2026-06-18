## ADDED Requirements

### Requirement: Dashboard consolidado del alumno
El sistema SHALL proveer una pantalla de dashboard para el alumno con una vista consolidada de todas sus materias, su progreso y alertas importantes.

#### Scenario: Dashboard muestra cards de materia con progreso
- **WHEN** el alumno autenticado accede a `/alumno/dashboard`
- **THEN** el sistema MUST mostrar una card por cada materia que cursa
- **AND** cada card MUST incluir: nombre de materia, nombre del profesor, barra de progreso (actividades aprobadas / total), indicador de estado (al día / atrasado / sin actividad)
- **AND** el sistema MUST llamar al endpoint `GET /api/alumno/dashboard`

#### Scenario: Dashboard muestra alertas y próximos eventos
- **WHEN** el alumno autenticado accede al dashboard
- **THEN** el sistema MUST mostrar alertas de: avisos no leídos (con contador), comunicaciones no leídas, coloquios con cupos abiertos próximos
- **AND** el sistema MUST mostrar los próximos eventos del calendario académico (parciales, TP, coloquios)

#### Scenario: Dashboard sin materias muestra estado vacío
- **WHEN** el alumno autenticado no tiene materias asignadas en el período actual
- **THEN** el sistema MUST mostrar un empty state con mensaje "No estás inscripto en ninguna materia en este período"

#### Scenario: Error en dashboard muestra estado de error
- **WHEN** el endpoint `GET /api/alumno/dashboard` falla
- **THEN** el sistema MUST mostrar un mensaje de error amigable con opción de reintentar

### Requirement: Endpoint GET /api/alumno/dashboard
El backend SHALL exponer un endpoint `GET /api/alumno/dashboard` que agregue los datos del dashboard del alumno autenticado.

#### Scenario: Endpoint retorna datos consolidados del alumno
- **WHEN** un usuario con permiso `estado-academico:ver` hace `GET /api/alumno/dashboard`
- **THEN** el endpoint MUST retornar: `materias` (array con id, nombre, profesor, progreso, estado), `avisos_no_leidos` (count), `comunicaciones_no_leidas` (count), `proximos_coloquios` (array), `proximas_fechas` (array)

#### Scenario: Endpoint rechaza acceso sin permiso
- **WHEN** un usuario SIN permiso `estado-academico:ver` hace `GET /api/alumno/dashboard`
- **THEN** el endpoint MUST retornar 403 Forbidden

#### Scenario: Endpoint respeta aislamiento multi-tenant
- **WHEN** el alumno del Tenant A hace `GET /api/alumno/dashboard`
- **THEN** el endpoint MUST retornar SOLO datos del Tenant A, no del Tenant B
