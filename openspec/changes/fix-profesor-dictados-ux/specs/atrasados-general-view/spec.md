## MODIFIED Requirements

### Requirement: Docente sees consolidated list of delayed students across all their subjects
The system SHALL render a consolidated page listing delayed students from all subjects assigned to the authenticated PROFESOR, fetched from the single endpoint `GET /api/v1/profesor/atrasados`, without requiring the teacher to navigate into a specific subject first. The page heading SHALL read "Desaprobados/Atrasados". Rows SHALL be grouped by alumno (`entrada_padron_id`): each alumno appears once, with all of that alumno's subjects shown comma-separated in a single "Materias" cell. Grouping is performed on the frontend; the backend endpoint SHALL remain unchanged.

#### Scenario: Page loads with all subjects' delayed students grouped by alumno
- **WHEN** a user with `atrasados:ver` permission opens the consolidated atrasados page
- **THEN** the system SHALL fetch all atrasados via `GET /api/v1/profesor/atrasados` (returning `AtrasadoGeneral[]`)
- **THEN** the page SHALL render one row per alumno (`entrada_padron_id`), not one row per (alumno, dictado)
- **THEN** each alumno's row SHALL list that alumno's `materia_nombre` values comma-separated
- **THEN** the page heading SHALL read "Desaprobados/Atrasados"

#### Scenario: Per-materia activity breakdown collapses under grouping
- **WHEN** an alumno is delayed in more than one materia
- **THEN** the alumno appears in a single grouped row with all materias comma-separated
- **AND** the per-materia `actividades_sin_entrega` breakdown collapses for that consolidated row (accepted tradeoff)

#### Scenario: Teacher with no delayed students sees empty state
- **WHEN** `GET /api/v1/profesor/atrasados` returns an empty list
- **THEN** the page SHALL display a positive confirmation message that there are no delayed students

#### Scenario: Filter by subject
- **WHEN** the teacher selects a subject from the filter dropdown
- **THEN** the table SHALL show only the grouped rows that include that subject
- **WHEN** the teacher clears the filter
- **THEN** the table SHALL show all grouped rows again

#### Scenario: Loading state while fetching
- **WHEN** the page is fetching data
- **THEN** a loading indicator SHALL be visible
- **WHEN** the fetch completes
- **THEN** the loading indicator SHALL disappear and the grouped table SHALL render

#### Scenario: User without atrasados:ver cannot access the page
- **WHEN** a user without `atrasados:ver` reaches the route
- **THEN** the system SHALL deny access via the route's AuthGuard

## ADDED Requirements

### Requirement: Consolidated atrasados view is labeled "Desaprobados/Atrasados"
The system SHALL label the cross-materia delayed-students entry point "Desaprobados/Atrasados" in the navigation sidebar and SHALL keep the corresponding sidebar test expectations in sync with the new label.

#### Scenario: Nav item label
- **WHEN** the sidebar renders the docente atrasados entry
- **THEN** its visible label SHALL be "Desaprobados/Atrasados"

#### Scenario: Sidebar test reflects the label
- **WHEN** `Sidebar.test.tsx` asserts on the atrasados nav item
- **THEN** its expectation SHALL match "Desaprobados/Atrasados"
