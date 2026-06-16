## Context

C-16 adds an internal task management system to the activia-trace platform. Tasks (`Tarea`) are tenant-scoped assignments between teachers and coordinators, with a state machine (Pendiente → En_progreso → Resuelta, Cancelada as terminal) and threaded comments (`ComentarioTarea`). Coordinators create and delegate tasks; teachers resolve them. The module mirrors a lightweight kanban-like workflow within the existing academic platform.

The permission `tareas:gestionar` is already defined in `Perm` at `backend/app/core/permissions.py` and seeded for PROFESOR, COORDINADOR, and ADMIN roles (from prior RBAC migration 003). No new permission seeds are needed.

All existing project conventions apply — same patterns used in C-15 (avisos), C-13 (encuentros), C-14 (evaluaciones):
- snake_case everywhere in Python
- SQLAlchemy 2.0 async with mixins (BaseMixin, TenantMixin, SoftDeleteMixin)
- Soft delete (no hard deletes)
- BaseRepository pattern with default tenant scoping
- Service layer with factory `create()` classmethod
- Router at `/api/v1/tareas` with `require_permission` guards
- Pydantic schemas with `extra='forbid'` and `from_attributes=True` for reads
- Alembic migration for schema changes (014)
- Tests with real PostgreSQL (no DB mocking)

## Goals / Non-Goals

**Goals:**
- Full CRUD for tasks (create, read, update state, soft-delete) for COORDINADOR/ADMIN
- Mis tareas view: list tasks assigned to current user, filterable by state and materia
- Global admin view: list all tasks per tenant, filterable by teacher, state, materia, free-text search
- State machine with validated transitions: Pendiente → En_progreso | Cancelada, En_progreso → Resuelta | Cancelada, Resuelta → En_progreso (coordinator return)
- Comment threads on tasks with author tracking
- Delegation traceability: `asignado_por` and `asignado_a` capture who assigned to whom
- Audit logging for all write operations

**Non-Goals:**
- No real-time notifications on state changes (audit trail suffices; push notifications are a future concern)
- No file attachments on tasks or comments
- No frontend implementation (this is backend-only)
- No task templates or recurring task generation
- No automatic reassignment rules

## Decisions

### D1: State machine pattern
Use the existing `StateMachine` from `app.core.state_machine` (already used by ComunicacionesService). The task state machine defines:

```
PENDIENTE → [EN_PROGRESO, CANCELADA]
EN_PROGRESO → [RESUELTA, CANCELADA]
RESUELTA → [EN_PROGRESO]  (coordinator returns for adjustments)
```

Only `CANCELADA` is terminal (no outgoing transitions). The `RESUELTA → EN_PROGRESO` transition is restricted to COORDINADOR/ADMIN — teachers cannot re-open.

### D2: Comment thread as separate table
`ComentarioTarea` is an append-only join table (no updates, no deletes). Each comment stores `tarea_id`, `autor_id`, `texto`, and `creado_at`. Comments are fetched ordered by `creado_at ASC` alongside the task. No denormalized count on `tarea`.

### D3: Delegation model
`Tarea` stores both `asignado_por` and `asignado_a` as direct FK references to `Usuario`. This is not a "reassign" model — a new task is created for each delegation. If a coordinator wants to reassign, they soft-delete the original and create a new one with `contexto_id` linking back (or simply create a new task). This preserves full audit trail.

### D4: Filtering strategy
Two query paths in the repository:
1. **Mis tareas** (`find_by_asignado(usuario_id, estado=None, materia_id=None)`) — filtered by `asignado_a`, with optional estado/materia filters. Always tenant-scoped.
2. **Admin view** (`find_all_managed(tenant_id, skip, limit, estado=None, materia_id=None, asignado_a_id=None, texto=None)`) — supports all filters including free-text search on `descripcion`. Tenant-scoped.

Text search uses SQL `ILIKE` on `descripcion` (high usage but moderate data volume; FTS can be added later if needed).

### D5: Existing Permissions used as-is
`tareas:gestionar` already exists in `Perm` enum and is seeded for PROFESOR, COORDINADOR, ADMIN roles (from 003 RBAC migration). All endpoints use this single permission. The router-level guard is `require_permission(Perm.TAREAS_GESTIONAR)`, with additional role-based logic in the service layer (e.g., re-open restricted to COORDINADOR/ADMIN).

### D6: Route prefix convention
Router uses `/api/v1/tareas` consistent with existing routers (`/api/v1/avisos`, `/api/v1/comunicaciones`, `/api/v1/encuentros`, etc.).

### D7: Migration sequence
The next migration is 014 (following 013 from C-15). It creates both `tarea` and `comentario_tarea` tables in one migration. Indexes:
- `tarea`: tenant_id + asignado_a + estado (composite for mis tareas queries)
- `tarea`: tenant_id + estado + materia_id (composite for admin filtered queries)
- `comentario_tarea`: tarea_id + creado_at (for ordered comment loading)

### D8: Soft delete behavior
Tarea uses `SoftDeleteMixin`. `ComentarioTarea` also uses soft delete — comments are never hard-deleted, preserving audit trail. When a task is soft-deleted, its comments remain (deleted_at is set on the task only). This matches the pattern used in Aviso/AcknowledgmentAviso from C-15.

## Risks / Trade-offs

- **[Risk] High query volume during peak periods**: Hundreds of simultaneous tasks with frequent state changes. **Mitigation**: Composite indexes on the most common filter paths (mis tareas by estado, admin by estado+materia). The `find_all_managed` endpoint supports pagination (offset/limit) and all filters are optional — no mandatory full-table scans.
- **[Risk] ILIKE text search performance**: Free-text search on `descripcion` via ILIKE will not scale to very large datasets. **Mitigation**: Acceptable for moderate task volume (tens of thousands). If needed later, migrate to PostgreSQL FTS or pg_trgm with trigram indexes without schema changes.
- **[Risk] No reassignment model**: Delegation creates a new task rather than reassigning. **Mitigation**: This is intentional for audit trail. The `contexto_id` field provides a lightweight link back to the originating task if traceability of delegations is needed. A future "reassign with history" feature can add a `tarea_historial` table.
- **[Trade-off] Single permission for all operations**: All endpoints use `tareas:gestionar` to keep RBAC simple. **Mitigation**: Service-layer checks handle role-based restrictions (e.g., only coordinator can re-open). If finer granularity is needed later, sub-permissions (`tareas:crear`, `tareas:asignar`, `tareas:resolver`) can be introduced without breaking existing code.
