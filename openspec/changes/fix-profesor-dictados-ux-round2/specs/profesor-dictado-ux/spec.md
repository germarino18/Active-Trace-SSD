## ADDED Requirements

### Requirement: Per-row individual comunicado in the per-dictado atrasados tab
The system SHALL provide a per-row "Comunicado individual" control in the per-dictado atrasados tab (`AtrasadosDictadoPage`), in addition to the existing per-subtipo general buttons. The control SHALL reuse the already-approved flexible comunicado pipeline (`useMutationComunicadoFlexible` → backend `prepare_comunicado_flexible` → `enqueue_masivo`), pre-scoped to that single alumno/atraso row. It SHALL NOT introduce any new send path and SHALL NOT bypass the comunicación approval gate.

#### Scenario: Per-row button opens the flexible comunicado form scoped to one alumno
- **WHEN** a PROFESOR clicks "Comunicado individual" on an atrasado row in the per-dictado atrasados tab
- **THEN** the existing `ComunicadoFlexibleForm` SHALL open pre-scoped to that single alumno/atraso
- **AND** submitting SHALL call `useMutationComunicadoFlexible` (the same mutation used by the cross-materia view), not a new mutation

#### Scenario: Approval gate is preserved
- **WHEN** the per-row individual comunicado is submitted
- **THEN** the comunicado SHALL enter the existing approval/enqueue pipeline unchanged
- **AND** no code path SHALL send a comunicado without passing through that gate

### Requirement: Actividad create and edit use a floating overlay modal
The system SHALL render the actividad create form AND a new actividad edit form inside a real overlay modal that floats above the actividades list. The modal SHALL be rendered via a React portal to `document.body`, use a `fixed inset-0` backdrop and an elevated z-index, and SHALL NOT be trapped inside the `overflow-hidden` activity cards or the tab scroll flow. The edit form SHALL allow changing an actividad's `fecha_limite` (nullable date) via `PATCH /api/v1/actividades/{actividad_id}`. Components SHALL stay under 200 LOC by factoring the modal and forms into sub-components.

#### Scenario: Modal floats above the list
- **WHEN** a PROFESOR opens the create or edit actividad modal
- **THEN** the modal SHALL render in a portal outside the activity-card subtree, above the list
- **AND** it SHALL be visible regardless of the tab's scroll position, with a backdrop

#### Scenario: Edit fecha_limite
- **WHEN** a PROFESOR edits an actividad and changes its `fecha_limite`
- **THEN** the system SHALL call `PATCH /api/v1/actividades/{actividad_id}` with the new date
- **AND** on success the modal SHALL close and the actividades list SHALL reflect the change

#### Scenario: Aprobado/controls use the design system
- **WHEN** the create or edit form renders its controls
- **THEN** they SHALL use the design-system components from `@/shared/components/ds`, not unstyled native controls

### Requirement: Actividad mutations invalidate actividades and atrasados caches
After creating, editing, or deleting an actividad in a dictado, the system SHALL invalidate BOTH the actividades query for that dictado AND the atrasados queries (per-dictado and cross-materia), because changing `fecha_limite` re-partitions which alumnos are atrasado.

#### Scenario: Edit fecha_limite refreshes atrasados
- **WHEN** a PROFESOR edits an actividad's `fecha_limite`
- **THEN** the system SHALL invalidate the actividades query for that dictado
- **AND** it SHALL invalidate the per-dictado atrasados query (`['profesor','atrasados',dictadoId]`) and the cross-materia atrasados query (`['profesor','atrasados-general']`)
- **AND** the atrasados panel SHALL show updated membership without a manual page reload

#### Scenario: Create and delete also invalidate both
- **WHEN** a PROFESOR creates or deletes an actividad
- **THEN** the system SHALL invalidate both the actividades query and the atrasados queries for the affected views
