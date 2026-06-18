## ADDED Requirements

### Requirement: Create recurring meeting slot
The system SHALL allow PROFESOR and COORDINADOR to define a recurring meeting slot with weekly periodicity for N weeks, automatically generating all instances (RN-13).

#### Scenario: Create recurring slot
- **WHEN** a PROFESOR creates a slot with subject "Álgebra", day "Monday", time "10:00", start date "2026-08-01", 15 weeks, and meet URL
- **THEN** the system generates 15 meeting instances (one per week)
- **AND** shows a success message with the count of generated instances

### Requirement: Create one-off meeting
The system SHALL allow PROFESOR and COORDINADOR to create a single meeting instance for a specific date and time without recurrence.

#### Scenario: Create one-off meeting
- **WHEN** a PROFESOR creates a one-off meeting with date "2026-08-15", time "14:00", and title "Consulta previa al parcial"
- **THEN** the system creates a single meeting instance

### Requirement: Edit meeting instance
The system SHALL allow PROFESOR and COORDINADOR to edit the state, meet URL, recording URL (available after the meeting), and internal comment of a meeting instance.

#### Scenario: Edit meeting state and URL
- **WHEN** a PROFESOR changes a meeting instance state to "Realizado" and adds a recording URL
- **THEN** the system updates the instance with the new state and recording URL

### Requirement: Generate LMS HTML block
The system SHALL generate a formatted HTML fragment of scheduled meetings, ready for publication in the LMS virtual classroom (F6.4).

#### Scenario: Generate HTML
- **WHEN** a PROFESOR clicks "Generar contenido para el aula virtual"
- **THEN** the system returns a formatted HTML block with all scheduled meetings for that subject
- **AND** shows a copy-to-clipboard button

### Requirement: Cross-tenant meeting overview
The system SHALL provide COORDINADOR and ADMIN with a transversal view of all meetings in the tenant, beyond the creating teacher's scope (F6.5).

#### Scenario: Admin overview
- **WHEN** an ADMIN accesses `/encuentros`
- **THEN** the system shows all meeting instances across all subjects and teachers
- **AND** provides filters by teacher, subject, state, and date range
