## Why

Coordinators and teachers need a lightweight internal task system to track follow-ups, pendings, and delegations within the academic platform — without relying on external tools. This enables full traceability of who assigned what to whom, state transitions with comments, and a unified view of pending work (F8.1–F8.3). The module is expected to handle hundreds of simultaneous tasks during peak academic periods.

## What Changes

- **New model `Tarea`**: tenant-scoped task with assigned-to/assigned-by, state machine (Pendiente→En_progreso→Resuelta, with Cancelada as terminal), optional materia and contexto references.
- **New model `ComentarioTarea`**: comment thread on a task with author reference and timestamp.
- **New Alembic migration**: creates `tarea` and `comentario_tarea` tables with indexes.
- **New repository `TareaRepository`**: CRUD + filtered queries by teacher, materia, state, free text, tenant-scoped.
- **New service `TareasService`**: create, assign/delegate with traceability, state transitions with machine validation, full filter-based listing, comment management, delegation audit trail.
- **New router `tareas.py`** at `/api/v1/tareas`: endpoints for CRUD, state transitions, comment threads, filtered listing (mis tareas + global admin view).
- **New schemas**: `TareaCreate`, `TareaRead`, `TareaUpdateEstado`, `ComentarioCreate`, `ComentarioRead`, `TareaFilterParams`, `TareaEstado`.
- **State machine** using existing `StateMachine` from `app.core.state_machine` with transitions:
  - Pendiente → En_progreso | Cancelada
  - En_progreso → Resuelta | Cancelada
  - Resuelta → En_progreso (coordinator returns for adjustments)
- **Audit events**: task creation, state change, comment addition, delegation via existing AuditLogger.
- **Permission usage**: `tareas:gestionar` (already exists in RBAC seed) guards all endpoints.

## Capabilities

### New Capabilities
- `tareas-crud`: Create, read, update (state + comments), soft-delete of internal tasks with tenant isolation.
- `tareas-mis-tareas`: Filtered listing of tasks assigned to the current user (mis tareas view) with state and materia filters.
- `tareas-admin`: Global admin/coordinator view of all tasks per tenant with full filtering by teacher, state, materia, free text.

### Modified Capabilities
- *(none — no existing specs change behaviorally)*

## Impact

- **New files**:
  - `backend/app/models/tarea.py`
  - `backend/app/repositories/tarea_repository.py`
  - `backend/app/services/tareas_service.py`
  - `backend/app/schemas/tareas.py`
  - `backend/app/api/v1/routers/tareas.py`
  - `backend/alembic/versions/014_create_tarea_tables.py`
- **Modified files**:
  - `backend/app/models/__init__.py` — register Tarea, ComentarioTarea
  - `backend/app/main.py` — register new router
- **No new permissions** — `tareas:gestionar` already exists in Perm enum and RBAC seed
