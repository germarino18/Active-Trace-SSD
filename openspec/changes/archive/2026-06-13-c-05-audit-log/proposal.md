## Why

activia-trace is a traceability platform — *trace* means **everything audits**. Today there is no immutable record of significant actions, and the legitimate impersonation capability promised by the security model (`03_actores_y_roles.md` §4) does not exist. Without an append-only audit log and proper impersonation attribution, the platform cannot satisfy its core security property: every meaningful action must be attributable to the real actor and impossible to erase. C-04 (RBAC) is archived, so the permission machinery this change depends on is ready.

## What Changes

- New `AuditLog` model (E-AUD), **append-only at both the application and the database layer**: no `update`/`delete` exposed by the repository, and a PostgreSQL trigger that rejects `UPDATE`/`DELETE` at the DB level.
- A reusable **audit helper** (`AuditLogger`) any service/endpoint can call to record a significant action with a standardized action code, JSON detail, affected-row count, and request metadata (IP / user-agent). Attribution always points to the **real actor**, even under impersonation.
- **Standardized action codes** as type-safe constants (`AccionAuditoria`): `IMPERSONACION_INICIAR`, `IMPERSONACION_FINALIZAR` (used now) plus forward-declared codes for future changes (`CALIFICACIONES_IMPORTAR`, `PADRON_CARGAR`, `COMUNICACION_ENVIAR`, `ASIGNACION_MODIFICAR`, `LIQUIDACION_CERRAR`).
- **Minimal functional impersonation** ("Option A"): a new `impersonacion:usar` permission, an optional `actor_id` JWT claim and `CurrentUser` field marking a distinguishable impersonation session, and two endpoints `POST /api/v1/auth/impersonate/{user_id}` and `POST /api/v1/auth/impersonate/end`. Both are tenant-scoped, permission-gated, and audited. **BREAKING** (cross-cutting): touches the already-archived C-03 auth area (`TokenService`, `get_current_user`) — flagged for explicit review.
- **Migration 004**: creates the `audit_log` table, installs the append-only DB trigger, and seeds the `impersonacion:usar` permission row into the existing `permiso` table (module `impersonacion`) for every tenant, following the migration-003 seed pattern.

## Capabilities

### New Capabilities
- `audit-log`: append-only audit trail model, repository, reusable logging helper, and standardized action codes.
- `impersonation`: legitimate, permission-gated, tenant-scoped impersonation with real-actor attribution and start/end audit entries.

### Modified Capabilities
<!-- No existing openspec spec describes auth/RBAC behavior at the requirement level; the impersonation changes to auth are documented as design cross-cutting impact, not a spec delta. -->

## Impact

- **New code**: `backend/app/models/audit_log.py`, `backend/app/repositories/audit_log_repository.py`, `backend/app/services/audit/audit_logger.py`, `backend/app/core/acciones_auditoria.py`, `backend/app/schemas/impersonation.py`, `backend/alembic/versions/004_*.py`.
- **Modified code (CRITICAL governance — explicit review required)**: `backend/app/schemas/auth.py` (`CurrentUser.actor_id`), `backend/app/services/auth/token_service.py` (`actor_id` claim), `backend/app/api/dependencies/auth.py` (`get_current_user` reads `actor_id`), `backend/app/core/permissions.py` (`Perm.IMPERSONACION_USAR`), `backend/app/api/v1/routers/auth.py` (impersonation endpoints).
- **Database**: new `audit_log` table + append-only trigger; new `impersonacion:usar` permission row per tenant.
- **Dependencies**: requires C-04 (`require_permission`, `permiso` table) — archived ✅. `materia_id` on `AuditLog` is nullable and unpopulated until the `Materia` entity exists (PA-01 open); this is a known, intentional gap.
- **Docs discrepancy**: the KB labels this "Migración 003"; 003 is already taken by C-04, so this change ships as **004**.
