## Context

activia-trace now has identity + 2FA (C-03) and fine-grained RBAC (C-04, archived). What is missing is the platform's defining property: an **immutable audit trail** (`08_arquitectura_propuesta.md` §3.4 "Audit log append-only") and the **legitimate impersonation** capability described in `03_actores_y_roles.md` §4 and §3.5. The data model for `AuditLog` (E-AUD) is fully specified in `04_modelo_de_datos.md` (lines 540–562), including the rule that no record may be modified or deleted and that impersonated actions record both the real actor and the impersonated user.

This is a CRITICAL-governance change: it touches auth (C-03, already archived) and creates the audit substrate. The propose step is the analysis/proposal deliverable; the cross-cutting auth modifications are flagged for explicit human review before application.

Existing building blocks this change reuses:
- `BaseRepository[Model]` with tenant scoping (`backend/app/repositories/base.py`) and the `RolPermisoRepository` style (`backend/app/repositories/rol_permiso_repository.py`).
- `BaseMixin` / `TenantMixin` (`backend/app/models/mixins.py`) — note: `AuditLog` does NOT use `SoftDeleteMixin`.
- `require_permission(...)` dependency + `Perm` constants (`backend/app/api/dependencies/permissions.py`, `backend/app/core/permissions.py`).
- `TokenService` (`backend/app/services/auth/token_service.py`) and `get_current_user` (`backend/app/api/dependencies/auth.py`), both from C-03.
- The migration-003 seed pattern (`backend/alembic/versions/003_create_rol_permiso_tables.py`).

### Constraints
- Reglas Duras #8 (identity ALWAYS from the verified JWT), #9 (tenant row-level scoping), #10 (RBAC fail-closed), #11 (Routers → Services → Repositories → Models), #13 (soft delete everywhere — **except** `AuditLog`, which is append-only by design and is never deleted), #16 (Strict TDD, real Postgres test DB, no DB mocks).
- Pydantic v2 schemas with `extra='forbid'`; snake_case; ≤500 LOC/file; one Alembic migration per schema change.

## Goals / Non-Goals

**Goals:**
- `AuditLog` model + table, append-only at the application layer (repository with only create/read) AND the database layer (trigger rejecting UPDATE/DELETE).
- A reusable `AuditLogger` helper that writes a record with correct real-actor / impersonated-user attribution derived from the verified session.
- `AccionAuditoria` action-code constants (impersonation codes used now; others forward-declared).
- Minimal functional impersonation ("Option A"): `actor_id` JWT claim + `CurrentUser` field, `impersonacion:usar` permission, and `impersonate` / `impersonate/end` endpoints, all tenant-scoped, permission-gated and audited.
- Migration 004: create `audit_log`, install the append-only trigger, seed `impersonacion:usar` per tenant.

**Non-Goals:**
- Populating `materia_id`: the `Materia` entity does not exist yet (PA-01 open). The column exists and is nullable; nothing in C-05 writes it. Known, intentional gap.
- Auto-instrumenting existing endpoints with audit calls beyond impersonation. The helper is delivered and proven; the features that emit `CALIFICACIONES_IMPORTAR`, `PADRON_CARGAR`, etc. live in later changes — those codes are forward-declared only.
- Audit-log read/list UI (frontend, C-21) and retention policies (KB states "sin límite de retención").
- Refresh-token rotation semantics for impersonation tokens beyond issuing a new access token (impersonation reuses the standard access-token flow).

## Decisions

### D1: Migration numbering is 004, not 003
**Chosen**: Ship as `004_create_audit_log_table.py`. It (a) creates `audit_log`, (b) installs the append-only DB trigger (see D2), and (c) INSERTs the `impersonacion:usar` permission row (module `impersonacion`) into the existing `permiso` table for every tenant, mirroring the per-tenant seed loop in migration 003.
**Why this is called out**: The KB (`04_modelo_de_datos.md` + the C-05 scope in CHANGES.md) labels this "Migración 003: audit_log", but `003_create_rol_permiso_tables.py` was already consumed by C-04 for the rol/permiso/rol_permiso tables and the permission-matrix seed. Numbering must continue at 004. The migration's `down_revision` chains to 003's revision id `c3d4e5f6a7b8`.
**Alternatives considered**:
- *Fold the audit table into a renamed 003*: impossible — 003 is archived and applied; renumbering would break the Alembic chain.
- *Two migrations (table, then seed)*: rejected; migration 003 already shows a single migration can create tables and seed in one `upgrade()` safely. One migration per schema change (Reglas Duras #15) is satisfied.

### D2: Append-only enforced in TWO layers
**Chosen**: Defense in depth.
- **App layer**: `AuditLogRepository(BaseRepository[AuditLog])` exposes only `create()` and read/list methods. It does NOT inherit or expose `update()`/`delete()`. (`BaseRepository` mutation methods, if any, are overridden to raise / not surfaced for this repo.)
- **DB layer**: migration 004 installs a PostgreSQL `BEFORE UPDATE OR DELETE` trigger function on `audit_log` that `RAISE EXCEPTION`s, so even a raw SQL statement or a future buggy code path cannot tamper with the trail.
**Why both**: The application layer protects ordinary code paths; the DB trigger is the real guarantee (it survives ORM misuse, raw SQL, and migrations). The test suite MUST exercise the DB layer with **raw SQL** (not only through the repository) to prove the DB defense actually fires — see tasks.md.
**Alternatives considered**:
- *App-layer only*: a single `session.execute(update(...))` or a DBA's `psql` session would silently break immutability. Rejected — insufficient for an audit trail.
- *PostgreSQL `RULE ... DO INSTEAD NOTHING`*: silently swallows the operation instead of erroring; an attacker/bug would believe the delete "worked". A trigger that RAISEs is louder and testable. Chosen trigger over rule.
- *Revoking UPDATE/DELETE grants on the role*: depends on connection role hygiene and is brittle across environments. The trigger is portable and self-contained in the migration.

### D3: Impersonation = "Option A" (minimal functional), via re-issued JWT
**Chosen**: Implement a working, auditable impersonation rather than docs/infra-only stubs.
- Add an optional `actor_id` claim to the access token and an optional `actor_id: UUID | None` field to `CurrentUser` (`backend/app/schemas/auth.py`). Absent `actor_id` ⇒ normal session (actor == `sub`).
- `TokenService.create_access_token` gains an optional `actor_id` parameter; when present it is embedded in the payload. `get_current_user` reads `actor_id` from the payload and populates `CurrentUser.actor_id` (still setting `TenantContext` from the token's `tenant_id`).
- New endpoints in `backend/app/api/v1/routers/auth.py`:
  - `POST /api/v1/auth/impersonate/{user_id}` — gated by `Depends(require_permission(Perm.IMPERSONACION_USAR))`; resolves the target user **within the caller's tenant** (Reglas Duras #9); issues an access token with `sub = target_user_id`, `actor_id = real_user_id`, target user's tenant; writes `IMPERSONACION_INICIAR` via `AuditLogger`.
  - `POST /api/v1/auth/impersonate/end` — valid only when the presented token has `actor_id`; re-issues a normal token for the real actor; writes `IMPERSONACION_FINALIZAR`.
**Identity compliance (Reglas Duras #8)**: identity always comes from a verified JWT. The endpoints comply because they **re-issue a new signed JWT**; they never accept an "act-as" header/param on subsequent requests. A stray act-as field on a normal request is ignored.
**Cross-cutting flag**: this modifies `TokenService` and `get_current_user` — CRITICAL auth territory whose owning change (C-03) is archived/closed. These edits are additive (optional claim/field, backward compatible: existing tokens have no `actor_id` and behave exactly as before) but MUST get explicit human review before application.
**Alternatives considered**:
- *Docs/infra-only impersonation (defer behavior)*: leaves a security-critical promise unimplemented and untestable; rejected.
- *Separate "impersonation token type" with its own purpose claim* (like the 2FA challenge token): heavier; `actor_id` presence already makes the session distinguishable without a parallel token kind. Rejected for now; can be layered later.
- *Server-side impersonation session table*: more auditable but adds state and a revocation surface; not needed for the minimal slice. Deferred.

### D4: Reusable `AuditLogger` helper with real-actor attribution
**Chosen**: An `AuditLogger` service (`backend/app/services/audit/audit_logger.py`) with a method like `log(*, current_user, accion, detalle, filas_afectadas, request, materia_id=None)` that builds and persists an `AuditLog` via `AuditLogRepository`. Attribution rule, derived from `CurrentUser`:
- If `current_user.actor_id` is set (impersonation): `actor_id = current_user.actor_id` (the REAL actor), `impersonado_id = current_user.user_id` (the impersonated user, i.e. `sub`).
- If `current_user.actor_id` is None (normal): `actor_id = current_user.user_id`, `impersonado_id = None`.
- `tenant_id` from `current_user.tenant_id`; `ip` / `user_agent` from the FastAPI `Request`; `materia_id` nullable (always None in C-05).
This keeps the KB rule — "toda acción bajo impersonación queda atribuida al actor real" — in exactly one place.
**Alternatives considered**:
- *A FastAPI dependency that auto-logs every request*: too coarse; only **significant** actions are audited, not every GET. Rejected.
- *Inlining the attribution logic at each call site*: duplicates the real-actor rule and invites it being gotten wrong. Rejected — centralize.

### D5: Action codes as `AccionAuditoria` constants (Perm-class pattern)
**Chosen**: A constants class in `backend/app/core/acciones_auditoria.py`, following the `Perm` pattern (`backend/app/core/permissions.py`):
```python
class AccionAuditoria:
    IMPERSONACION_INICIAR = "IMPERSONACION_INICIAR"
    IMPERSONACION_FINALIZAR = "IMPERSONACION_FINALIZAR"
    # forward-declared for future changes:
    CALIFICACIONES_IMPORTAR = "CALIFICACIONES_IMPORTAR"
    PADRON_CARGAR = "PADRON_CARGAR"
    COMUNICACION_ENVIAR = "COMUNICACION_ENVIAR"
    ASIGNACION_MODIFICAR = "ASIGNACION_MODIFICAR"
    LIQUIDACION_CERRAR = "LIQUIDACION_CERRAR"
```
Only the two impersonation codes are emitted in C-05; the rest are declared so later changes reference a constant, not a literal (matching the KB action-code catalog at `04_modelo_de_datos.md` lines 643–657). `Perm.IMPERSONACION_USAR = "impersonacion:usar"` is added to the existing `Perm` class.
**Alternatives considered**:
- *A DB-backed action-code catalog* (like roles/permisos): the KB calls the catalog "administrable", but action codes are emitted from code, not configured per tenant; a string constant is the right source of truth for the emitter. A DB catalog can be added later for documentation without changing emitters. Deferred.
- *Python `Enum`*: fine, but the codebase already uses plain string-constant classes (`Perm`); match the established convention.

## Risks / Trade-offs

- **Cross-cutting auth edit on an archived change (C-03)** → Mitigation: changes are additive and backward compatible (`actor_id` optional everywhere; pre-existing tokens unaffected). Flagged for explicit human review per CRITICAL governance before application. C-03's auth tests must stay green as a safety net.
- **DB trigger could block legitimate operations** (e.g. a future need to mask PII in a record) → Mitigation: by design the trail is immutable (KB rule); any future redaction must be a new appended record, never an in-place edit. The trigger is the contract.
- **Trigger downgrade must be reversible** → Mitigation: migration 004 `downgrade()` drops the trigger and function before dropping the table; tested via up/down in CI.
- **`materia_id` is dead weight until PA-01 closes** → Mitigation: nullable column, documented Non-Goal; no code writes it, no test asserts on it.
- **Impersonation token reuse window** → Mitigation: impersonation issues a normal-TTL access token; an audited `IMPERSONACION_FINALIZAR` plus short access-token TTL bound exposure. A server-side revocation/session model is a deferred enhancement (D3 alternative).
- **`extra='forbid'` on `CurrentUser`**: adding `actor_id` is safe, but any serializer relying on the old shape must tolerate the new optional field → Mitigation: default `None`, covered by tests on both normal and impersonation sessions.

## Migration Plan

1. Apply migration 004: creates `audit_log` (with `BaseMixin` + `tenant_id` columns, `materia_id` nullable, NO `deleted_at`), creates indexes (`tenant_id`, `fecha_hora`), installs the append-only trigger function + trigger, seeds `impersonacion:usar` per existing tenant.
2. Deploy backend with the additive auth changes (`actor_id` claim/field), the `AuditLogger`, `AuditLogRepository`, `AccionAuditoria`, and the two impersonation endpoints.
3. **Rollback**: `downgrade()` drops the trigger, the trigger function, the `impersonacion:usar` seed rows, and the `audit_log` table; the additive auth code is backward compatible, so reverting the deploy leaves existing tokens valid.

## Open Questions

- **PA-01 (Materia entity)**: blocks any code that would populate `materia_id`; intentionally unaddressed here.
- **Server-side impersonation revocation**: do we need a session/blocklist to revoke an impersonation token before its TTL expires? Deferred (D3 alternative); revisit if audit/compliance requires hard revocation.
- **Action-code DB catalog**: whether to mirror `AccionAuditoria` into an administrable DB catalog for documentation. Deferred; emitters stay code-constant-driven.
