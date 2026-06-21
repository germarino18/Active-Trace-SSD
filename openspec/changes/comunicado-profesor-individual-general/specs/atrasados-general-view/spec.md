## ADDED Requirements

### Requirement: Docente can send an individual communication from a row in the consolidated atrasados view
The consolidated atrasados view SHALL offer, in each student row, a control to compose and send a communication addressed only to that student, pre-filling that student's identity and their overdue/failed materias.

#### Scenario: Open individual comunicado from a row
- **WHEN** the teacher clicks the per-row "Enviar comunicado" action for a given student
- **THEN** the system SHALL open a comunicado form scoped to that student (that student's `entrada_padron_id` + `dictado_id`)
- **THEN** the form SHALL display the student's overdue/failed materias, derived client-side from the consolidated atrasados data (`GET /api/v1/profesor/atrasados`) by matching `entrada_padron_id`
- **THEN** the activity selector SHALL be OPTIONAL

#### Scenario: Submit individual comunicado
- **WHEN** the teacher submits the individual comunicado form
- **THEN** the system SHALL call `POST /api/v1/profesor/comunicado-atrasados-flexible` with a single-element `destinatarios` list and the optional `actividad_id`
- **THEN** on success the system SHALL show the resulting total and lote reference

### Requirement: Docente can send a general communication to all delayed students from the consolidated view
The consolidated atrasados view SHALL offer a top-level action that sends the same communication to ALL listed delayed students (desaprobados + atrasados) across materias.

#### Scenario: Send to all
- **WHEN** the teacher clicks the top-level "Enviar a todos" action and submits the form
- **THEN** the system SHALL call `POST /api/v1/profesor/comunicado-atrasados-flexible` with a `destinatarios` list containing every currently listed student
- **THEN** the activity selector SHALL be OPTIONAL
- **THEN** on success the system SHALL show the aggregated total of enqueued communications

#### Scenario: Respect the active subject filter for the general send
- **WHEN** a subject filter is active and the teacher triggers "Enviar a todos"
- **THEN** the `destinatarios` list SHALL include only the students currently shown under that filter

### Requirement: Activity is optional in the consolidated-view comunicado form
The comunicado form opened from the consolidated atrasados view SHALL allow submission without selecting an activity.

#### Scenario: Submit without an activity
- **WHEN** the teacher submits the form leaving the activity selector empty
- **THEN** the system SHALL send the request with `actividad_id` null and SHALL NOT block submission on the activity field
