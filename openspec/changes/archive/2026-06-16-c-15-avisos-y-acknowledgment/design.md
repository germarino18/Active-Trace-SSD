## Context

C-15 adds a broadcast announcement system to the activia-trace platform. Avisos are tenant-scoped messages that can target users by role, course (materia), cohort (cohorte), or globally. They support an optional acknowledgment requirement (requiere_ack) that tracks per-user read confirmation.

The project already has permission constants `avisos:publicar` and `avisos:confirmar` defined in `Perm` and seeded in the RBAC migration (003), with COORDINADOR/ADMIN granted `avisos:publicar` and all roles granted `avisos:confirmar`.

All existing project conventions apply:
- snake_case everywhere in Python
- SQLAlchemy 2.0 async with mixins (BaseMixin, TenantMixin, SoftDeleteMixin)
- Soft delete (no hard deletes)
- BaseRepository pattern with tenant scoping
- Service layer with factory `create()` method
- Router at `/api/v1/avisos` with `require_permission` guards
- Pydantic schemas with `extra='forbid'` and `from_attributes=True` for reads
- Alembic migration for schema changes (013 in the sequence)
- Tests with real PostgreSQL (no DB mocking)

## Goals / Non-Goals

**Goals:**
- Full CRUD for avisos (create, read, update, soft-delete) for COORDINADOR/ADMIN
- Filtered listing of visible avisos for the requesting user based on their role, enrollment (cohorte/materia), and the aviso's alcance, inicio_en/fin_en window, and active flag
- Acknowledgment: users confirm reading; system tracks who confirmed when, deriving counters from the join table (no denormalized counts on `aviso`)
- Audit logging for all write operations
- Visibility rules: only active avisos within their ini-en/fin_en window are shown; audience is resolved by role + alcance scope

**Non-Goals:**
- No real-time push notifications or WebSocket broadcasts
- No scheduled publication/deadactivation (client-side filtering by the visibility window on each read)
- No frontend implementation (this is backend-only)
- No email/WhatsApp/SMS delivery — avisos are in-app only
- No denormalized confirmation counters on the aviso table itself

## Decisions

### D1: Soft delete pattern
All existing models use `SoftDeleteMixin`. Aviso and AcknowledgmentAviso will follow the same pattern. `AcknowledgmentAviso` soft delete enables undeletion of an aviso without losing acknowledgment audit trail.

### D2: Audience resolution strategy
Instead of pre-computing target user lists, each aviso stores `alcance` + optional foreign keys (`materia_id`, `cohorte_id`, `rol_destino`). At query time, the service resolves the current user's roles and enrollments (via `Usuario` → roles, and cohorte/materia via `Dictado`/`Asignacion` if needed) and matches against the aviso's target criteria. This avoids synchronization issues if user enrollments change.

### D3: Acknowledgment as a separate table
`AcknowledgmentAviso` is an append-only join table. Counters (total acks, pending) are derived via SQL `COUNT` queries from this table. No counter column on `aviso` itself — prevents drift between the counter and actual data.

### D4: No state machine needed
Unlike Comunicacion (which has a state machine with Pendiente→Enviando→Enviado), Aviso is simpler: it's either active or soft-deleted. The `activo` boolean and `inicio_en`/`fin_en` window control visibility. No multi-step workflow.

### D5: Existing Permissions used as-is
Both `avisos:publicar` and `avisos:confirmar` already exist in the RBAC seed (003) and Perm enum. No new migration is needed for permissions. COORDINADOR/ADMIN have `avisos:publicar` (write access). All roles have `avisos:confirmar` (acknowledgment access).

### D6: Route prefix convention
The router uses `/api/v1/avisos` consistent with existing routers (`/api/v1/comunicaciones`, `/api/v1/estructura`, etc.).

### D7: Migration sequence
The next migration is 013 (following 012 from C-14). It creates both `aviso` and `acknowledgment_aviso` tables in one migration. Indexes: tenant-scoped lookup on alcance+activo, acknowledgment lookup on aviso_id+usuario_id.

## Risks / Trade-offs

- **[Risk] Audience query performance**: Resolving audience at query time (joining usuario_rol, asignacion, dictado) could be slow for tenants with many users. **Mitigation**: Indexes on the scope columns (alcance, materia_id, cohorte_id, rol_destino). If performance degrades, pre-computed audience cache can be added later without schema changes.
- **[Risk] Soft delete on AcknowledgmentAviso**: If an aviso is deleted and recreated, old acknowledgments for the deleted aviso are still in the DB (soft-deleted). **Mitigation**: This is desired behavior for audit trail. The deleted_at filter prevents stale acks from affecting active queries.
- **[Trade-off] No cascading audience change**: If a user's enrollment changes (e.g., drops a course), previously visible avisos may remain visible until the visibility window ends. Acceptable because avisos are broadcast messages, not per-user assignments.
