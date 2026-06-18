## ADDED Requirements

### Requirement: Backend — GET /api/admin/analytics/tendencias/atrasados-por-cohorte

The system SHALL expose a GET endpoint at `/api/admin/analytics/tendencias/atrasados-por-cohorte` returning a time series of overdue students grouped by cohort.

**Filtros**: `fecha_desde` (date), `fecha_hasta` (date), `carrera_id` (UUID, optional), `cohorte_id` (UUID, optional). All filters are query params.

**Response**: `[{fecha: "2025-03-01", cohorte: "2024", total_atrasados: 12, total_alumnos: 45, porcentaje: 26.67}]` — ordered by fecha ASC, cohorte ASC.

The system SHALL require permission `auditoria:ver` to access this endpoint.

#### Scenario: Returns time series for default period (last 12 months)
- **WHEN** GET `/api/admin/analytics/tendencias/atrasados-por-cohorte` without filters
- **THEN** response is 200 with monthly data points for the last 12 months, grouped by cohort

#### Scenario: Filters by cohorte_id
- **WHEN** GET `/api/admin/analytics/tendencias/atrasados-por-cohorte?cohorte_id=<uuid>`
- **THEN** response only includes rows for that cohorte

#### Scenario: Returns empty array when no data matches
- **WHEN** GET `/api/admin/analytics/tendencias/atrasados-por-cohorte?fecha_desde=2000-01-01&fecha_hasta=2000-01-31`
- **THEN** response is 200 with an empty array

#### Scenario: Returns 403 without auditoria:ver permission
- **WHEN** user without `auditoria:ver` calls the endpoint
- **THEN** response is 403 Forbidden

### Requirement: Backend — GET /api/admin/analytics/tendencias/distribucion-notas

The system SHALL expose a GET endpoint at `/api/admin/analytics/tendencias/distribucion-notas` returning nota distribution as a histogram.

**Filtros**: `dictado_id` (UUID, optional), `materia_id` (UUID, optional), `cohorte_id` (UUID, optional). All query params.

**Response**: `[{rango: "0-25%", cantidad: 10}, {rango: "26-50%", cantidad: 15}, {rango: "51-75%", cantidad: 20}, {rango: "76-100%", cantidad: 30}]` — ordered by rango ASC.

The system SHALL require permission `auditoria:ver` to access this endpoint.

#### Scenario: Returns distribution for all materias when no filters
- **WHEN** GET `/api/admin/analytics/tendencias/distribucion-notas`
- **THEN** response is 200 with 4 buckets covering 0-100%

#### Scenario: Filters by specific dictado
- **WHEN** GET `/api/admin/analytics/tendencias/distribucion-notas?dictado_id=<uuid>`
- **THEN** response only includes that dictado's notas

#### Scenario: Returns zeros for empty buckets
- **WHEN** no notas exist for the given filters
- **THEN** response includes all 4 buckets with cantidad: 0

### Requirement: Backend — GET /api/admin/analytics/dashboard

The system SHALL expose a GET endpoint at `/api/admin/analytics/dashboard` returning a consolidated view of KPIs and summary trend data for the analytics homepage.

**Response**: `{total_alumnos: 500, total_atrasados_actual: 45, promedio_general: 72.5, alumnos_en_riesgo: {bajo: 350, medio: 100, alto: 50}, tendencia_atrasados_ultimo_mes: [{fecha, total}], total_materias: 20}`.

The system SHALL require permission `auditoria:ver` to access this endpoint.

#### Scenario: Returns consolidated dashboard data
- **WHEN** GET `/api/admin/analytics/dashboard`
- **THEN** response is 200 with all KPI fields populated

#### Scenario: Returns 403 without auditoria:ver
- **WHEN** user without `auditoria:ver` calls the endpoint
- **THEN** response is 403 Forbidden

### Requirement: Frontend — Página de dashboard de tendencias

The system SHALL render a page at `/admin/analytics` displaying:
- KPI cards (total alumnos, atrasados actuales, promedio general, materias activas)
- Line chart: atrasados por cohorte vs tiempo (Recharts `<LineChart>`)
- Bar chart: distribución de notas (Recharts `<BarChart>`)
- Filters: carrera, cohorte, rango de fechas, materia
- All charts react to filter changes

#### Scenario: Page loads with default data
- **WHEN** user navigates to `/admin/analytics`
- **THEN** page renders KPIs, line chart, bar chart with default (last 12 months) data

#### Scenario: Filters update charts
- **WHEN** user changes a filter value (e.g., cohorte)
- **THEN** all charts re-fetch and re-render with filtered data

#### Scenario: Shows loading state while fetching
- **WHEN** data is being fetched
- **THEN** shows skeleton/loading indicators

#### Scenario: Shows empty state when no data
- **WHEN** no data matches the filters
- **THEN** charts show "Sin datos disponibles" overlay

### Requirement: Frontend — Lazy loading and routing

The analytics page SHALL be lazy-loaded in `App.tsx`. The sidebar SHALL include a navigation item for Analytics under "Métricas" with icon `insights` and permission `auditoria:ver`.

#### Scenario: Route is lazy-loaded
- **WHEN** user navigates to `/admin/analytics`
- **THEN** the chunk for `AnalyticsDashboardPage` is loaded on demand

#### Scenario: Sidebar item visible with correct permission
- **WHEN** user has `auditoria:ver` permission
- **THEN** sidebar shows "Analytics" item with icon `insights`

#### Scenario: Sidebar item hidden without permission
- **WHEN** user does NOT have `auditoria:ver` permission
- **THEN** sidebar hides the Analytics item
