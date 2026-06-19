## ADDED Requirements

### Requirement: NEXO routes render placeholder pages instead of 404
The system SHALL register the routes `/nexo/atrasados`, `/nexo/encuentros`, and `/nexo/tareas` in the router. Each SHALL render a stub page informing the user the feature is under development, and SHALL be protected by the corresponding NEXO permission.

#### Scenario: NEXO user visits /nexo/atrasados
- **WHEN** a user with `nexo:atrasados:ver` navigates to `/nexo/atrasados`
- **THEN** the system SHALL render a page with a clear heading "Atrasados — NEXO"
- **THEN** the page SHALL display a message indicating this view is under development
- **THEN** the page SHALL include a link or button to return to the dashboard
- **THEN** the HTTP status SHALL be 200 (no 404)

#### Scenario: NEXO user visits /nexo/encuentros
- **WHEN** a user with `nexo:encuentros:ver` navigates to `/nexo/encuentros`
- **THEN** the system SHALL render a page with heading "Encuentros — NEXO" and an "en desarrollo" message

#### Scenario: NEXO user visits /nexo/tareas
- **WHEN** a user with `nexo:tareas:ver` navigates to `/nexo/tareas`
- **THEN** the system SHALL render a page with heading "Tareas — NEXO" and an "en desarrollo" message

#### Scenario: User without NEXO permission cannot access NEXO routes
- **WHEN** a user without any `nexo:*` permission navigates to any `/nexo/*` route
- **THEN** the system SHALL redirect to `/forbidden`
