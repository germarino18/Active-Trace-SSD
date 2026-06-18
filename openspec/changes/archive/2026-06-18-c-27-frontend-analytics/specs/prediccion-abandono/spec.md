## ADDED Requirements

### Requirement: Backend — GET /api/admin/analytics/prediccion/abandono

The system SHALL expose a GET endpoint at `/api/admin/analytics/prediccion/abandono` returning per-alumno risk assessment.

**Filtros**: `cohorte_id` (UUID, optional), `materia_id` (UUID, optional), `riesgo` (string enum: "bajo" | "medio" | "alto", optional).

**Algoritmo rule-based** (sin ML):
- ALTO: ≥3 materias con atrasos activos AND promedio general < umbral (default 60%)
- MEDIO: 1-2 materias con atrasos OR promedio general < umbral
- BAJO: sin atrasos AND promedio general ≥ umbral

**Query param**: `umbral` (int, optional, default 60) — el promedio mínimo considerado "normal".

**Response**: `[{alumno_id: "<uuid>", alumno_nombre: "Juan Pérez", materia: "Matemáticas", promedio: 45.5, atrasos: 3, riesgo: "alto"}]` — ordered by riesgo DESC (alto first), then promedio ASC.

The system SHALL require permission `auditoria:ver` to access this endpoint.

#### Scenario: Returns risk list for all alumnos without filters
- **WHEN** GET `/api/admin/analytics/prediccion/abandono`
- **THEN** response is 200 with array of alumno risk assessments

#### Scenario: Filters by risk level
- **WHEN** GET `/api/admin/analytics/prediccion/abandono?riesgo=alto`
- **THEN** response only includes alumnos classified as ALTO

#### Scenario: Filters by cohorte
- **WHEN** GET `/api/admin/analytics/prediccion/abandono?cohorte_id=<uuid>`
- **THEN** response only includes alumnos from that cohorte

#### Scenario: Custom umbral parameter
- **WHEN** GET `/api/admin/analytics/prediccion/abandono?umbral=70`
- **THEN** the ALTO/MEDIO classification uses 70% as the threshold instead of default 60%

#### Scenario: Returns empty array when no matches
- **WHEN** GET `/api/admin/analytics/prediccion/abandono?riesgo=alto` and no alumnos match
- **THEN** response is 200 with empty array

#### Scenario: Returns 403 without auditoria:ver
- **WHEN** user without `auditoria:ver` calls the endpoint
- **THEN** response is 403 Forbidden

### Requirement: Frontend — Tabla de predicción de abandono

The system SHALL render a table component on the analytics dashboard showing per-alumno risk with:
- Columns: Nombre, Materia, Promedio, Atrasos, Riesgo (badge colored)
- Color coding: ALTO → red bg (`bg-error/10` + `text-error`), MEDIO → amber (`bg-warning/10` + `text-warning`), BAJO → green (`bg-success/10` + `text-success`)
- Filters above the table: cohorte, materia, riesgo
- Sortable by promedio, atrasos, riesgo

#### Scenario: Table renders with risk data
- **WHEN** data is loaded from `prediccion/abandono` endpoint
- **THEN** table shows each alumno with color-coded risk badges

#### Scenario: Filters narrow results
- **WHEN** user selects "ALTO" in riesgo filter
- **THEN** table only shows high-risk alumnos

#### Scenario: Empty state
- **WHEN** no alumnos match filters
- **THEN** table shows "No se encontraron alumnos con los filtros seleccionados"

#### Scenario: Loading state
- **WHEN** data is being fetched
- **THEN** table shows skeleton rows
