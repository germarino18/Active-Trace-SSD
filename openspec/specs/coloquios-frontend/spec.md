## ADDED Requirements

### Requirement: Create convocation
The system SHALL allow COORDINADOR and ADMIN to create an oral exam convocation defining subject, instance, available days with slots and quotas per day.

#### Scenario: Create convocation
- **WHEN** a COORDINADOR creates a convocation with subject "Álgebra", instance "1", and 3 days with 10 slots each
- **THEN** the system creates the convocation with 30 total available slots across 3 days
- **AND** shows the convocation in the list with metrics

### Requirement: Import students to convocation
The system SHALL allow COORDINADOR and ADMIN to load or update the roster of students eligible for a specific convocation (F7.2).

#### Scenario: Import students
- **WHEN** a COORDINADOR uploads a student roster for a convocation
- **THEN** the system associates the students with the convocation
- **AND** shows "N alumnos cargados exitosamente"

### Requirement: List convocations with metrics
The system SHALL display a tabular view of all active convocations with operational metrics: subject, instance, available days, convocados, active reservations, and free slots (F7.4).

#### Scenario: View convocations list
- **WHEN** a COORDINADOR accesses `/coloquios`
- **THEN** the system shows a table with columns: materia, instancia, días disponibles, convocados, reservas activas, and cupos libres
- **AND** each row has management action buttons

### Requirement: Metrics panel
The system SHALL expose convocation metrics: total students loaded, active instances, active reservations, and registered grades (F7.1).

#### Scenario: View metrics
- **WHEN** a COORDINADOR opens a convocation detail page
- **THEN** the system shows KPI cards: total alumnos, instancias activas, reservas, cupos libres

### Requirement: Student self-reservation
The system SHALL allow ALUMNO users to reserve a slot in a convocation for an available day with quota. A reservation SHALL decrement the available quota (FL-07).

#### Scenario: Reserve slot successfully
- **WHEN** an ALUMNO selects an available day with quota > 0 and confirms reservation
- **THEN** the system creates a reservation with estado "Activa"
- **AND** decrements the available quota by 1

#### Scenario: No quota available
- **WHEN** an ALUMNO attempts to reserve a fully booked day
- **THEN** the system shows "No hay cupos disponibles para este día"

### Requirement: Consolidated results
The system SHALL display consolidated oral exam results (F7.5).

#### Scenario: View results
- **WHEN** an ADMIN accesses a convocation's results tab
- **THEN** the system shows each student's reservation and grade status
