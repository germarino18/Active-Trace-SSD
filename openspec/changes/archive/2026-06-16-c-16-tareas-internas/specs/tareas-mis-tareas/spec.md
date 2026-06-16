## ADDED Requirements

### Requirement: GET /api/v1/tareas/mias (list tasks assigned to current user)
The system SHALL provide an endpoint that returns tasks assigned to the authenticated user. The endpoint SHALL support optional query filters:
- `estado`: filter by one or more states
- `materia_id`: filter by materia UUID
- `texto`: free-text search on descripcion (ILIKE)

Results SHALL be paginated (offset/limit). Default ordering SHALL be by creado_at DESC (newest first). The `asignado_a` filter is ALWAYS set to the current user's ID — it cannot be overridden.

#### Scenario: List my pending tasks
- **WHEN** calling GET /api/v1/tareas/mias?estado=PENDIENTE
- **THEN** the response is 200 with a paginated list of tasks where asignado_a matches current user AND estado=PENDIENTE

#### Scenario: List my tasks with materia filter
- **WHEN** calling GET /api/v1/tareas/mias?materia_id=<uuid>
- **THEN** the response is 200 with tasks filtered by both asignado_a and materia_id

#### Scenario: List my tasks with free-text search
- **WHEN** calling GET /api/v1/tareas/mias?texto=seguimiento
- **THEN** the response is 200 with tasks where descripcion ILIKE '%seguimiento%' and asignado_a matches current user

#### Scenario: My tasks paginated
- **WHEN** calling GET /api/v1/tareas/mias?offset=0&limit=10
- **THEN** the response is 200 with up to 10 tasks and total count

#### Scenario: Cannot override asignado_a filter
- **WHEN** calling GET /api/v1/tareas/mias with an invalid or missing authorization
- **THEN** the response is 401 Unauthorized; the asignado_a is always derived from the JWT
