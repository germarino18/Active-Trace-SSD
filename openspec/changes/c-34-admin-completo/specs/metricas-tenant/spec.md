## ADDED Requirements

### Requirement: Endpoint de métricas del tenant
El sistema SHALL exponer `GET /api/admin/metricas` (gated por `estructura:gestionar`) que devuelva KPIs agregados del tenant: total de alumnos, alumnos activos, porcentaje de alumnos en riesgo, promedio de progreso general, total de docentes, total de materias activas, total de carreras activas. Los datos SHALL calcularse en vivo mediante consultas agregadas, no almacenarse en tablas separadas.

#### Scenario: Métricas calculadas en vivo
- **WHEN** un ADMIN invoca `GET /api/admin/metricas`
- **THEN** el sistema responde con KPIs calculados de las tablas del tenant

#### Scenario: Tenant sin datos
- **WHEN** un ADMIN invoca métricas en un tenant sin alumnos ni docentes
- **THEN** el sistema responde con valores en cero (no error)
