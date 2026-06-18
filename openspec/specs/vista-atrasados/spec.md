## ADDED Requirements

### Requirement: PROFESOR can view overdue students
The system SHALL display a table of students whose grades are below the configured threshold or who have missing activities for the selected materia.

#### Scenario: Overdue students table
- **WHEN** the PROFESOR navigates to `/materias/{id}/atrasados`
- **THEN** the system calls `GET /api/v1/materias/{id}/atrasados`
- **THEN** the system displays a table with columns: student name, email, commission, pending activities count, current grade, threshold, status (atrasado / al día)
- **THEN** the table is sortable by any column
- **THEN** rows with status "atrasado" are visually highlighted

#### Scenario: Empty overdue list
- **WHEN** there are no overdue students for the materia
- **THEN** the system displays a message "No hay alumnos atrasados en esta materia"

### Requirement: PROFESOR can view student ranking
The system SHALL display a ranked table of students sorted by the number of approved activities.

#### Scenario: Ranking view
- **WHEN** the PROFESOR selects the "Ranking" tab
- **THEN** the system calls `GET /api/v1/materias/{id}/ranking`
- **THEN** the system displays a table sorted by approved activity count (descending)
- **THEN** each row shows: rank position, student name, approved count, total activities, percentage

### Requirement: PROFESOR can view final grades
The system SHALL aggregate activities and calculate a final grade per student for the selected materia.

#### Scenario: Final grades view
- **WHEN** the PROFESOR selects the "Notas finales" tab
- **THEN** the system calls `GET /api/v1/materias/{id}/notas-finales`
- **THEN** the system displays a table with: student name, final grade, status (aprobado / desaprobado)
- **THEN** the table is exportable (the user can copy or download the data)

### Requirement: PROFESOR can view quick reports
The system SHALL display summary metrics for the selected materia.

#### Scenario: Quick reports view
- **WHEN** the PROFESOR selects the "Reportes" tab
- **THEN** the system calls `GET /api/v1/materias/{id}/reportes-rapidos`
- **THEN** the system displays metric cards: total students, at-risk count, average completion percentage, activities count
- **WHEN** there are no imported grades
- **THEN** the system shows an informational state "No hay datos importados para esta materia"
