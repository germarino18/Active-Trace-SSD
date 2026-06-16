## ADDED Requirements

### Requirement: GET /api/v1/tareas (admin list all tasks)
The system SHALL provide an endpoint that returns all tasks for the current tenant, accessible only to COORDINADOR and ADMIN roles. The endpoint SHALL support optional query filters:
- `estado`: filter by one or more states
- `materia_id`: filter by materia UUID
- `asignado_a_id`: filter by assigned teacher UUID
- `texto`: free-text search on descripcion (ILIKE)

Results SHALL be paginated (offset/limit). Default ordering SHALL be by creado_at DESC (newest first).

#### Scenario: Admin lists all tasks with estado filter
- **WHEN** calling GET /api/v1/tareas?estado=EN_PROGRESO
- **THEN** the response is 200 with all tasks in EN_PROGRESO state for the current tenant

#### Scenario: Admin filters by teacher
- **WHEN** calling GET /api/v1/tareas?asignado_a_id=<teacher_uuid>
- **THEN** the response is 200 with tasks assigned to that specific teacher

#### Scenario: Admin filters by materia
- **WHEN** calling GET /api/v1/tareas?materia_id=<uuid>
- **THEN** the response is 200 with tasks for that materia

#### Scenario: Admin combines multiple filters
- **WHEN** calling GET /api/v1/tareas?estado=PENDIENTE&materia_id=<uuid>&asignado_a_id=<teacher_uuid>
- **THEN** the response is 200 with tasks matching all filters

#### Scenario: Admin free-text search
- **WHEN** calling GET /api/v1/tareas?texto=urgente
- **THEN** the response is 200 with tasks whose descripcion ILIKE '%urgente%'

#### Scenario: Admin paginated listing
- **WHEN** calling GET /api/v1/tareas?offset=0&limit=20
- **THEN** the response is 200 with up to 20 tasks and total count

#### Scenario: PROFESOR gets 403 on admin listing
- **WHEN** a PROFESOR calls GET /api/v1/tareas (without /mias)
- **THEN** the response is 403 Forbidden
