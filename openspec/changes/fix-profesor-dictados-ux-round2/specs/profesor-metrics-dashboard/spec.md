## ADDED Requirements

### Requirement: Profesor live metrics live at a dedicated /profesor-dashboard route
The system SHALL serve the live PROFESOR metrics (Materias asignadas, Alumnos en riesgo, Encuentros) at a dedicated `/profesor-dashboard` route rendered by a new `ProfesorMetricsDashboardPage`, which SHALL own the `useProfesorDashboard` data call. The generic `/dashboard` route SHALL revert to rendering only the static `ROLE_CONFIG` for every role and SHALL NOT call `useProfesorDashboard`. A navbar entry SHALL link to `/profesor-dashboard`, and a PROFESOR SHALL be directed to it.

#### Scenario: Profesor metrics render at /profesor-dashboard
- **WHEN** a PROFESOR navigates to `/profesor-dashboard`
- **THEN** `ProfesorMetricsDashboardPage` SHALL render the live metrics via `useProfesorDashboard`
- **AND** a navbar entry SHALL link to `/profesor-dashboard`

#### Scenario: Generic dashboard reverts to static config
- **WHEN** any user (including a PROFESOR) navigates to `/dashboard`
- **THEN** the page SHALL render the generic static `ROLE_CONFIG` view
- **AND** it SHALL NOT call `useProfesorDashboard`

#### Scenario: Existing dictado routes are untouched
- **WHEN** a PROFESOR navigates to `/dictados` or `/dictados/:dictadoId`
- **THEN** those routes and their tabs SHALL behave exactly as before this change
