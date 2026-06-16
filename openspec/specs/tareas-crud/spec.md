## ADDED Requirements

### Requirement: Tarea SQLAlchemy model with state machine
The system SHALL define a `Tarea` SQLAlchemy model with the following columns, inheriting from BaseMixin, TenantMixin, SoftDeleteMixin:
- `materia_id`: UUID, nullable FK → Materia (null if institutional, not course-specific)
- `asignado_a`: UUID, NOT NULL FK → Usuario (who must resolve the task)
- `asignado_por`: UUID, NOT NULL FK → Usuario (who creates/assigns the task)
- `estado`: ENUM, NOT NULL — one of `PENDIENTE`, `EN_PROGRESO`, `RESUELTA`, `CANCELADA`. Default `PENDIENTE`.
- `descripcion`: TEXT, NOT NULL
- `contexto_id`: UUID, nullable — optional reference to another domain entity

The model SHALL use a `StateMachine` from `app.core.state_machine` with the following allowed transitions:
- PENDIENTE → [EN_PROGRESO, CANCELADA]
- EN_PROGRESO → [RESUELTA, CANCELADA]
- RESUELTA → [EN_PROGRESO] (coordinator return for adjustments)
- CANCELADA: terminal state, no outgoing transitions

#### Scenario: Create task with required fields
- **WHEN** creating a Tarea with valid descripcion, tenant_id, asignado_a, and asignado_por
- **THEN** the task is persisted with estado=PENDIENTE and a UUID id

#### Scenario: Create task with optional materia and contexto
- **WHEN** creating a Tarea with optional materia_id and contexto_id
- **THEN** both nullable fields are stored as provided

#### Scenario: Transition from PENDIENTE to EN_PROGRESO
- **WHEN** a task in PENDIENTE state transitions to EN_PROGRESO
- **THEN** the transition succeeds and estado becomes EN_PROGRESO

#### Scenario: Transition from EN_PROGRESO to RESUELTA
- **WHEN** a task in EN_PROGRESO state transitions to RESUELTA
- **THEN** the transition succeeds and estado becomes RESUELTA

#### Scenario: Transition from EN_PROGRESO to CANCELADA
- **WHEN** a task in EN_PROGRESO state transitions to CANCELADA
- **THEN** the transition succeeds and estado becomes CANCELADA

#### Scenario: Transition from RESUELTA to EN_PROGRESO (coordinator return)
- **WHEN** a task in RESUELTA state transitions to EN_PROGRESO
- **THEN** the transition succeeds and estado becomes EN_PROGRESO

#### Scenario: Invalid transition PENDIENTE to RESUELTA
- **WHEN** attempting to transition a task from PENDIENTE directly to RESUELTA
- **THEN** a TransitionError is raised

#### Scenario: Terminal state CANCELADA rejects all transitions
- **WHEN** attempting any transition from CANCELADA
- **THEN** a TransitionError is raised

#### Scenario: Tenant isolation on task queries
- **WHEN** querying tasks in tenant A
- **THEN** only tasks with tenant_id = A are returned

### Requirement: ComentarioTarea SQLAlchemy model
The system SHALL define a `ComentarioTarea` SQLAlchemy model with the following columns, inheriting from BaseMixin, TenantMixin, SoftDeleteMixin:
- `tarea_id`: UUID, NOT NULL FK → Tarea
- `autor_id`: UUID, NOT NULL FK → Usuario
- `texto`: TEXT, NOT NULL
- `creado_at`: TIMESTAMPTZ, NOT NULL, auto-generated

ComentarioTarea SHALL be append-only: no update or hard-delete operations are exposed.

#### Scenario: Add comment to existing task
- **WHEN** creating a ComentarioTarea with valid tarea_id, autor_id, and texto
- **THEN** the comment is persisted with auto-generated creado_at timestamp

#### Scenario: Comments ordered by creation time
- **WHEN** fetching comments for a task
- **THEN** they are ordered by creado_at ASC

### Requirement: POST /api/v1/tareas (create task)
The system SHALL provide an endpoint to create a new task. Only COORDINADOR and ADMIN roles may create tasks. The endpoint SHALL accept `asignado_a` (UUID), `descripcion` (text), optional `materia_id` (UUID), and optional `contexto_id` (UUID). The `asignado_por` SHALL be derived from the authenticated user.

#### Scenario: Coordinator creates task
- **WHEN** a COORDINADOR calls POST /api/v1/tareas with valid asignado_a, descripcion
- **THEN** the response is 201 with the created Tarea

#### Scenario: PROFESOR cannot create task
- **WHEN** a PROFESOR calls POST /api/v1/tareas
- **THEN** the response is 403 Forbidden

### Requirement: PATCH /api/v1/tareas/{id}/estado (state transition)
The system SHALL provide an endpoint to transition a task's state. The endpoint SHALL accept `estado` (new state) and optional `comentario` (text). If `comentario` is provided, a ComentarioTarea SHALL be auto-created. The `RESUELTA → EN_PROGRESO` transition SHALL be restricted to COORDINADOR/ADMIN.

#### Scenario: Change state and add auto-comment
- **WHEN** calling PATCH /api/v1/tareas/{id}/estado with estado=EN_PROGRESO and comentario="Starting work"
- **THEN** the response is 200, estado is EN_PROGRESO, and a ComentarioTarea is created with the provided text

#### Scenario: Invalid state transition returns 422
- **WHEN** calling PATCH /api/v1/tareas/{id}/estado with an invalid transition (e.g., PENDIENTE → RESUELTA)
- **THEN** the response is 422 with a validation error

### Requirement: GET /api/v1/tareas/{id} (get single task with comments)
The system SHALL provide an endpoint to retrieve a single task by ID, including its comment thread.

#### Scenario: Get task with comments
- **WHEN** calling GET /api/v1/tareas/{id} with a valid task ID
- **THEN** the response is 200 with the task details and all comments ordered by creado_at ASC

### Requirement: DELETE /api/v1/tareas/{id} (soft-delete task)
The system SHALL provide an endpoint to soft-delete a task. Only COORDINADOR/ADMIN may delete.

#### Scenario: Soft delete task
- **WHEN** calling DELETE /api/v1/tareas/{id}
- **THEN** the response is 204 and the task's deleted_at is set
