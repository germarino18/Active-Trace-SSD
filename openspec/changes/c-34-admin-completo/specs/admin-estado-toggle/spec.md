## ADDED Requirements

### Requirement: Toggle de estado para carreras, cohortes, materias y dictados
El sistema SHALL exponer endpoints `PATCH /api/admin/{recurso}/{id}/estado` para los recursos `carreras`, `cohortes`, `materias` y `dictados`. Cada endpoint SHALL alternar el estado entre `Activa` e `Inactiva` (o `Activo`/`Inactivo` para dictados). Todos gated por `estructura:gestionar`. La operación SHALL registrarse en el audit log.

#### Scenario: Alternar carrera a Inactiva
- **WHEN** un ADMIN invoca `PATCH /api/admin/carreras/{id}/estado` sobre una carrera Activa
- **THEN** la carrera pasa a estado Inactiva y se registra en auditoría

#### Scenario: Alternar dictado a Activo
- **WHEN** un ADMIN invoca `PATCH /api/admin/dictados/{id}/estado` sobre un dictado Inactivo
- **THEN** el dictado pasa a estado Activo y se registra en auditoría

### Requirement: Consistencia de carrera activa para cohortes abiertas
El sistema SHALL mantener la regla de negocio existente: una cohorte abierta (`vig_hasta` nulo) NO puede pertenecer a una carrera Inactiva. Al cambiar una carrera a Inactiva, el sistema SHALL rechazar la operación si existen cohortes abiertas asociadas.

#### Scenario: Rechazar toggle si hay cohortes abiertas
- **WHEN** un ADMIN intenta cambiar una carrera a Inactiva que tiene cohortes abiertas
- **THEN** el sistema rechaza con error de validación (422) y la carrera permanece Activa
