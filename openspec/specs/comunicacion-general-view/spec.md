## ADDED Requirements

### Requirement: Docente sees a communications hub aggregated across all subjects
The system SHALL provide a route `/comunicacion` that renders a hub page showing the status of all communications (sent, pending, failed, cancelled) grouped by subject, with a link to initiate new communications per subject.

#### Scenario: Page loads with communications by subject
- **WHEN** a user with `comunicacion:ver` permission navigates to `/comunicacion`
- **THEN** the system SHALL fetch subjects assigned to the teacher (`GET /api/v1/materias/`)
- **THEN** for each subject, the system SHALL fetch communication statuses (`GET /api/v1/comunicaciones/?materia_id={id}`)
- **THEN** the page SHALL display a card or table row per subject showing: nombre de materia, total enviados, total pendientes, total fallidos, total cancelados
- **THEN** each row SHALL include a "Comunicar" action that navigates to `/materias/:id/comunicar`

#### Scenario: No communications sent yet
- **WHEN** the teacher has subjects but no communications have been sent to any of them
- **THEN** the page SHALL display a message "Aún no enviaste comunicaciones. Seleccioná una materia para comenzar."
- **THEN** each subject row SHALL show counters at zero and a "Comunicar" CTA

#### Scenario: User without comunicacion:ver cannot access the route
- **WHEN** a user without `comunicacion:ver` navigates to `/comunicacion`
- **THEN** the system SHALL redirect to `/forbidden`

#### Scenario: Communications with pending items are visually highlighted
- **WHEN** a subject has one or more communications with status `pendiente`
- **THEN** the pending count SHALL be rendered with a warning color or badge to draw attention
