## ADDED Requirements

### Requirement: Aviso CRUD
The system SHALL allow COORDINADOR and ADMIN to create, read, update, and delete announcements (avisos) with the following fields: title, message, scope (Global/Materia/Cohorte/Rol), severity (info/warning/critical), validity start/end dates, ordering priority, and mandatory acknowledgment flag.

#### Scenario: Create aviso with Global scope
- **WHEN** a COORDINADOR creates an aviso with scope "Global", severity "warning", and validity "2026-07-01" to "2026-12-31"
- **THEN** the system saves the aviso and shows it in the avisos list
- **AND** all users in the tenant see this aviso

#### Scenario: Create aviso with Materia scope
- **WHEN** an ADMIN creates an aviso with scope "Materia" and selects "Álgebra"
- **THEN** only users assigned to "Álgebra" see this aviso

#### Scenario: Edit aviso
- **WHEN** a COORDINADOR edits an existing aviso's message and saves
- **THEN** the system updates the aviso and shows a success toast

#### Scenario: Delete aviso
- **WHEN** a COORDINADOR confirms deletion of an aviso
- **THEN** the system soft-deletes the aviso

### Requirement: Aviso visualization with scope filtering
The system SHALL display visible avisos to each user based on their roles, scope assignments, and cohort memberships (RN-18, RN-19, RN-20). Avisos outside their validity window SHALL NOT be shown.

#### Scenario: SCOPE_POR_ROL visibility
- **WHEN** a PROFESOR views their avisos and an aviso with SCOPE_POR_ROL → PROFESOR exists and is within validity
- **THEN** the aviso is displayed in the PROFESOR's aviso list

#### Scenario: Out of validity window
- **WHEN** today's date is after `vigencia_hasta` of an aviso
- **THEN** the aviso is NOT displayed

#### Scenario: Multiple scope match
- **WHEN** a user has role PROFESOR and is also assigned to a materia that matches an aviso's scope
- **THEN** the aviso is displayed once (no duplicates)

### Requirement: Acknowledgment confirmation
The system SHALL allow users to confirm reading an aviso when `requiere_ack` is true. Acknowledged avisos SHALL cease to be displayed as pending.

#### Scenario: Acknowledge aviso
- **WHEN** a user clicks "Confirmar lectura" on an aviso with `requiere_ack: true`
- **THEN** the system records the acknowledgment timestamp
- **AND** the aviso is no longer shown as pending for that user

#### Scenario: Ack counter display
- **WHEN** a COORDINADOR views the aviso list
- **THEN** each aviso shows a counter: "15/30 confirmado(s)" (confirmed / total required based on scope)
