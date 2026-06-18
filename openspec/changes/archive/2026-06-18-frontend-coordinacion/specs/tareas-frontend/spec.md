## ADDED Requirements

### Requirement: My tasks view
The system SHALL show a user their own assigned tasks, filterable by academic context (subject, cohort), with the ability to initiate delegation or escalate to coordination.

#### Scenario: View my tasks
- **WHEN** a PROFESOR navigates to `/tareas`
- **THEN** the system shows a list of tasks assigned to them, sorted by creation date descending

#### Scenario: Filter my tasks by subject
- **WHEN** a PROFESOR selects subject filter "Álgebra"
- **THEN** the system shows only tasks related to subjects within Álgebra's academic context

#### Scenario: Initiate delegation
- **WHEN** a PROFESOR clicks "Delegar" on a task
- **THEN** the system opens a delegation form to reassign the task to another teacher

### Requirement: Assign and delegate tasks
The system SHALL allow PROFESOR and COORDINADOR to create and delegate tasks to other teaching team members, maintaining traceability of the original assigner.

#### Scenario: Create and assign task
- **WHEN** a COORDINADOR creates a task with title, description, assigned user, and academic context
- **THEN** the system creates the task with estado "Pendiente" and logs asignado_por
- **AND** the assigned user sees the task in their "My Tasks" view

#### Scenario: Delegate with traceability
- **WHEN** user A delegates a task to user B
- **THEN** the system changes `asignado_a` to user B
- **AND** the system preserves `asignado_por` as user A
- **AND** the task's comment thread records the delegation event

### Requirement: Task state workflow
The system SHALL support the following task states: Pendiente → En progreso → Resuelta → Cancelada, with valid transitions enforced.

#### Scenario: Progress task
- **WHEN** a user changes a task from "Pendiente" to "En progreso"
- **THEN** the system updates the task state and records the transition

#### Scenario: Resolve task
- **WHEN** a user changes a task from "En progreso" to "Resuelta"
- **THEN** the system updates the state and optionally accepts a resolution comment

#### Scenario: Cancel task
- **WHEN** a user changes a task from any state to "Cancelada"
- **THEN** the system requires a cancellation reason
- **AND** the task is marked as final

#### Scenario: Invalid transition
- **WHEN** a user attempts to change "Resuelta" back to "Pendiente"
- **THEN** the system rejects the transition with an error message

### Requirement: Task comment thread
The system SHALL allow adding comments to a task as part of the async workflow.

#### Scenario: Add comment to task
- **WHEN** a user adds a comment to a task
- **THEN** the comment is appended to the task's thread with author, timestamp, and content

#### Scenario: View comment thread
- **WHEN** a user opens a task detail page
- **THEN** the system displays all comments in chronological order, newest first

### Requirement: Global admin task view
The system SHALL provide COORDINADOR and ADMIN a global view of all tasks in the tenant with filters for assigned teacher, assigner, subject, state, and free text search.

#### Scenario: Filter by state
- **WHEN** an ADMIN selects filter state "En progreso"
- **THEN** the system shows only tasks in "En progreso" state

#### Scenario: Free text search
- **WHEN** a COORDINADOR types "examen" in the search field
- **THEN** the system shows tasks where title or description contains "examen"
