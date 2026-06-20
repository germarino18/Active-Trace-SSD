## ADDED Requirements

### Requirement: PROFESOR dictado views are reached under /dictados
The system SHALL serve the PROFESOR dictado LIST at `/dictados` and the dictado detail at `/dictados/:dictadoId`, preserving the per-section children (`alumnos`, `actividades`, `atrasados`, `equipo`) and the existing permission gating. The legacy `/profesor/dashboard` and `/profesor/dictados/:dictadoId` locations SHALL no longer be the canonical routes for these views.

#### Scenario: List renders at /dictados
- **WHEN** a PROFESOR with the required permission navigates to `/dictados`
- **THEN** the dictado list (`ProfesorDashboardListPage`) SHALL render
- **AND** the "Mis Dictados" nav item SHALL link to `/dictados`

#### Scenario: Detail and its sections render under /dictados/:dictadoId
- **WHEN** a PROFESOR navigates to `/dictados/:dictadoId`
- **THEN** the dictado detail SHALL render and redirect its index to the `alumnos` section
- **AND** the children `alumnos`, `actividades`, `atrasados`, `equipo` SHALL each render at `/dictados/:dictadoId/<section>`

#### Scenario: Permission gating is preserved
- **WHEN** a user without the required dictado permission navigates to `/dictados` or `/dictados/:dictadoId`
- **THEN** the AuthGuard SHALL block access exactly as it did on the legacy routes

### Requirement: Dictado views display the dictado human name, not its UUID
The system SHALL display a dictado's human name as `Materia — Cohorte` in the detail header and SHALL render the `:dictadoId` breadcrumb segment with that name while the browser URL keeps the UUID. A dictado corresponds to exactly one cohorte; the cohorte SHALL be rendered through a flexible (array-shaped) structure so that multiple cohortes would be a future no-op, but the data SHALL remain single.

#### Scenario: Header shows Materia — Cohorte
- **WHEN** a PROFESOR opens `/dictados/:dictadoId`
- **THEN** the header SHALL show `Materia — Cohorte` using `materia_nombre` and `cohorte_nombre`
- **AND** the header SHALL NOT show the literal text "Panel del Dictado" nor "ID: {uuid}"

#### Scenario: Breadcrumb shows the dictado name for the UUID segment
- **WHEN** the current path contains a dictado UUID segment (e.g. `/dictados/4551f5a8-...`)
- **THEN** the breadcrumb SHALL render the dictado's `Materia — Cohorte` name for that segment
- **AND** the browser URL SHALL still contain the UUID

#### Scenario: Name source unavailable falls back gracefully
- **WHEN** the dictado name is not yet loaded
- **THEN** the breadcrumb/header SHALL render a neutral placeholder (not the raw UUID) until the name resolves

### Requirement: Padrón supports per-row alumno removal
The system SHALL provide a per-row delete control in the dictado padrón that performs a single soft-delete (`DELETE /api/v1/profesor/dictados/{id}/padron/alumnos/{entrada_padron_id}`), in addition to the existing bulk baja. Removing an alumno SHALL keep the alumno's calificaciones and return them to the disponibles pool.

#### Scenario: Remove a single alumno from the padrón
- **WHEN** a PROFESOR clicks the per-row delete control for an alumno and confirms
- **THEN** the system SHALL call the single-baja endpoint for that `entrada_padron_id`
- **AND** the padrón list SHALL refresh without that alumno
- **AND** that alumno SHALL reappear in the disponibles pool

#### Scenario: Bulk baja reproduction is required before any bug fix
- **WHEN** the reported "bulk baja doesn't work" issue is investigated
- **THEN** a runtime reproduction SHALL be performed before any code fix is written
- **AND** if the bulk path is confirmed broken at runtime, the root cause SHALL be fixed; if it works at runtime, the per-row control SHALL be the delivered remedy

### Requirement: Registrar nota appears inline in the target activity
The system SHALL render the "Registrar nota" input as a new row inside the selected activity's table, pre-filled with that actividad. The alumno selector SHALL list ONLY alumnos who are not already graded in that activity. The "aprobado" controls in both the create row and the edit row SHALL use the design system style rather than a vanilla checkbox.

#### Scenario: Inline row scoped to the chosen activity
- **WHEN** a PROFESOR triggers "Registrar nota" for a given actividad
- **THEN** the input SHALL appear as a new row within that activity's table, not at the top of the page
- **AND** the actividad SHALL be pre-selected from `registrarNotaActividadId`

#### Scenario: Only ungraded alumnos are selectable
- **WHEN** the inline registrar-nota row is open for an actividad
- **THEN** the alumno selector SHALL exclude every alumno who already has a calificacion matching that activity (by `entrada_padron_id`)
- **AND** if all alumnos are already graded, the selector SHALL be empty / disabled

#### Scenario: Aprobado control uses the design system
- **WHEN** the create row or edit row renders its "aprobado" control
- **THEN** it SHALL use the design system styling, not an unstyled native checkbox

### Requirement: Dictado mutations refresh metrics and atrasados
After any actividad, calificacion, or alumno mutation in a dictado, the system SHALL invalidate the dictado metrics, the profesor dashboard, the per-dictado atrasados, and the cross-materia atrasados caches so the stat cards and atrasados panel re-fetch.

#### Scenario: Mutation refreshes dependent views
- **WHEN** a PROFESOR adds/removes an alumno (single or bulk), creates/deletes an actividad, registers/edits a calificacion, or uploads a calificaciones CSV
- **THEN** the system SHALL invalidate `['profesor','metricas',dictadoId]`, `['profesor','dashboard']`, `['profesor','atrasados',dictadoId]`, and `['profesor','atrasados-general']`
- **AND** the stat cards and the atrasados panel SHALL show updated values without a manual page reload

#### Scenario: Every mutation hook is covered
- **WHEN** the profesor mutation hooks are audited
- **THEN** every mutation hook listed above SHALL include the metrics/dashboard/atrasados invalidations
