## ADDED Requirements

### Requirement: Docente sees consolidated list of delayed students across all their subjects
The system SHALL provide a route `/atrasados` that renders a page listing delayed students from all subjects assigned to the authenticated teacher, without requiring the teacher to navigate into a specific subject first.

#### Scenario: Page loads with all subjects' delayed students
- **WHEN** a user with `atrasados:ver` permission navigates to `/atrasados`
- **THEN** the system SHALL fetch all subjects assigned to the teacher (`GET /api/v1/materias/`)
- **THEN** for each subject, the system SHALL fetch delayed students (`GET /api/v1/calificaciones/{materiaId}/atrasados`)
- **THEN** the page SHALL display a unified table with columns: Alumno, Materia, Actividades aprobadas, % Aprobación, Estado
- **THEN** each row SHALL link to the subject detail page (`/materias/:id/atrasados`) for drill-down

#### Scenario: Teacher with no delayed students sees empty state
- **WHEN** all subjects return an empty atrasados list
- **THEN** the page SHALL display a positive confirmation message "No hay alumnos atrasados en ninguna de tus materias"

#### Scenario: Filter by subject
- **WHEN** the teacher selects a subject from the filter dropdown
- **THEN** the table SHALL show only the delayed students from that subject
- **WHEN** the teacher clears the filter
- **THEN** the table SHALL show all delayed students again

#### Scenario: Loading state while fetching
- **WHEN** the page is fetching data from any subject
- **THEN** a loading indicator SHALL be visible
- **WHEN** all fetches complete
- **THEN** the loading indicator SHALL disappear and the table SHALL render

#### Scenario: User without atrasados:ver cannot access the route
- **WHEN** a user without `atrasados:ver` navigates to `/atrasados`
- **THEN** the system SHALL redirect to `/forbidden`
