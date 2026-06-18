## ADDED Requirements

### Requirement: PROFESOR/TUTOR can view a follow-up monitor
The system SHALL display a filterable view of student activity status for the selected materia.

#### Scenario: Monitor view with filters
- **WHEN** the PROFESOR or TUTOR navigates to `/materias/{id}/monitor`
- **THEN** the system calls `GET /api/v1/materias/{id}/monitor` with the current filter parameters
- **THEN** the system displays filter inputs: student name (text search), commission (dropdown), activity (dropdown), minimum completion percentage (number)
- **THEN** the system displays a results table: student name, email, commission, activities completed count, total activities, completion percentage, status

#### Scenario: Apply filters
- **WHEN** the PROFESOR modifies any filter and clicks "Aplicar filtros"
- **THEN** the system calls `GET /api/v1/materias/{id}/monitor` with the updated filter parameters
- **THEN** the table updates with filtered results

#### Scenario: Clear filters
- **WHEN** the PROFESOR clicks "Limpiar filtros"
- **THEN** all filter inputs are reset to their default values
- **THEN** the table shows unfiltered results

#### Scenario: Empty monitor results
- **WHEN** no students match the applied filters
- **THEN** the system displays "No se encontraron alumnos con los filtros seleccionados"
