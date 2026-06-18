## ADDED Requirements

### Requirement: My teams view
The system SHALL provide a "My Teams" view for PROFESOR, TUTOR, NEXO, and COORDINADOR showing their own assignments with role, career, cohort, associated commissions, validity period, and status.

#### Scenario: User sees own assignments
- **WHEN** a user with role PROFESOR navigates to `/equipos`
- **THEN** the system displays a list of their assignments with materia, carrera, cohorte, rol, vigencia, and estado columns

#### Scenario: Empty state
- **WHEN** a user has no active assignments
- **THEN** the system shows an empty state message: "No tenés asignaciones activas"

#### Scenario: Role-based access
- **WHEN** an ALUMNO accesses `/equipos`
- **THEN** the system returns a 403 forbidden page

### Requirement: Assignment CRUD
The system SHALL allow COORDINADOR and ADMIN to create, read, update, and delete individual assignments with filters by materia, carrera, cohorte, user identifier, teacher name, role, and report relation.

#### Scenario: Create individual assignment
- **WHEN** a COORDINADOR submits the assignment form with user, materia, carrera, cohorte, role, and validity dates
- **THEN** the system creates the assignment and shows it in the assignment list
- **AND** the system logs an AUDIT action `ASIGNACION_MODIFICAR`

#### Scenario: Filter assignments
- **WHEN** a COORDINADOR selects "PROFESOR" role filter
- **THEN** the system displays only PROFESOR assignments

#### Scenario: Delete assignment
- **WHEN** a COORDINADOR confirms deletion of an assignment
- **THEN** the system soft-deletes the assignment and shows a success toast
- **AND** the system logs an AUDIT action `ASIGNACION_MODIFICAR`

### Requirement: Bulk assignment
The system SHALL allow COORDINADOR and ADMIN to select multiple teachers and assign them in bulk to a materia × carrera × cohorte × role combination with a defined validity period (RN-30).

#### Scenario: Bulk assign multiple teachers
- **WHEN** a COORDINADOR selects 3 teachers, materia "Álgebra", career "Ingeniería", cohort "MAR-2026", role "PROFESOR", and submits
- **THEN** the system creates 3 assignments in a single transaction
- **AND** shows a success modal with count of assignments created
- **AND** the system logs exactly one AUDIT action `ASIGNACION_MODIFICAR` with `filas_afectadas: 3`

#### Scenario: Skip already assigned teachers
- **WHEN** a COORDINADOR attempts bulk assignment and 1 of 3 teachers is already assigned
- **THEN** the system creates 2 new assignments and shows "2 asignaciones creadas, 1 ya existente omitido"

### Requirement: Clone team between periods
The system SHALL allow COORDINADOR and ADMIN to clone a teaching team from one cohort to another, duplicating active assignments with new dates and excluding expired ones (RN-12).

#### Scenario: Clone team successfully
- **WHEN** a COORDINADOR selects source cohort "MAR-2025" and destination cohort "MAR-2026" for materia "Álgebra"
- **THEN** the system creates assignment copies with updated dates
- **AND** shows a success modal with count of cloned assignments
- **AND** the system logs exactly one AUDIT action

#### Scenario: No active assignments to clone
- **WHEN** the source cohort has no active assignments for the selected materia
- **THEN** the system shows "No hay asignaciones activas para clonar"

### Requirement: Modify team validity
The system SHALL allow COORDINADOR and ADMIN to modify the general validity dates of a teaching team in bulk.

#### Scenario: Bulk validity change
- **WHEN** a COORDINADOR changes the end date for a team's assignments from "2026-07-01" to "2026-08-01"
- **THEN** the system updates all active assignments for that equipo (materia_id, carrera_id, cohorte_id) with the new end date

### Requirement: Export team as CSV
The system SHALL allow COORDINADOR and ADMIN to download a CSV file of a teaching team's assignments (D8).

#### Scenario: Download CSV
- **WHEN** a COORDINADOR clicks "Exportar equipo" for "Álgebra - MAR-2026"
- **THEN** the system downloads a CSV file with columns: docente, email, rol, comisiones, vigencia_desde, vigencia_hasta, estado
