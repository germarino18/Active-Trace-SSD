# Tasks — C-05 audit-log

> Strict TDD: every implementation task is RED → GREEN → TRIANGULATE → REFACTOR.
> Real Postgres test DB, no DB mocks (Reglas Duras #4/#16). CRITICAL governance: the
> auth-touching tasks (group 5) require explicit human review before writing code.

## 1. Action codes & permission constant

- [x] 1.1 RED: test that `AccionAuditoria.IMPERSONACION_INICIAR` / `IMPERSONACION_FINALIZAR` resolve to their codes and that the forward-declared codes (`CALIFICACIONES_IMPORTAR`, `PADRON_CARGAR`, `COMUNICACION_ENVIAR`, `ASIGNACION_MODIFICAR`, `LIQUIDACION_CERRAR`) exist
- [x] 1.2 GREEN: create `backend/app/core/acciones_auditoria.py` with the `AccionAuditoria` class (D5)
- [x] 1.3 RED+GREEN: test and add `Perm.IMPERSONACION_USAR = "impersonacion:usar"` to `backend/app/core/permissions.py`

## 2. AuditLog model & migration 004

- [x] 2.1 RED: model test — `AuditLog` has columns `tenant_id`, `fecha_hora`, `actor_id`, `impersonado_id`, `materia_id` (nullable), `accion`, `detalle` (JSONB), `filas_afectadas`, `ip`, `user_agent`; uses `BaseMixin` + `TenantMixin`; has NO `deleted_at` (append-only, not soft-deleted)
- [x] 2.2 GREEN: create `backend/app/models/audit_log.py` and register it in `backend/app/models/__init__.py`
- [x] 2.3 Write migration `backend/alembic/versions/004_create_audit_log_table.py` with `down_revision = "c3d4e5f6a7b8"` (D1): create `audit_log` table + indexes (`tenant_id`, `fecha_hora`)
- [x] 2.4 In migration 004 `upgrade()`: install the PostgreSQL `BEFORE UPDATE OR DELETE` trigger function on `audit_log` that `RAISE EXCEPTION` (D2)
- [x] 2.5 In migration 004 `upgrade()`: seed `impersonacion:usar` permission (module `impersonacion`) per existing tenant, following the migration-003 seed loop (D1)
- [x] 2.6 In migration 004 `downgrade()`: drop trigger → trigger function → `impersonacion:usar` seed rows → `audit_log` table
- [x] 2.7 Test migration up/down applies cleanly against the test DB (table created then fully removed)

## 3. AuditLogRepository (append-only, app layer)

- [x] 3.1 RED: test `AuditLogRepository.create()` persists a record tenant-scoped and returns it
- [x] 3.2 RED: test the repository exposes NO `update`/`delete` method (introspection / attribute absence)
- [x] 3.3 GREEN: create `backend/app/repositories/audit_log_repository.py` extending `BaseRepository[AuditLog]` with only create + read/list, no mutation surface (D2)
- [x] 3.4 TRIANGULATE: test tenant-scoped list returns only the caller-tenant's records (Reglas Duras #9)

## 4. Database-level append-only enforcement (raw SQL)

- [x] 4.1 RED: test that a raw SQL `UPDATE audit_log SET ...` on an existing row raises a DB error and leaves the row unchanged
- [x] 4.2 RED: test that a raw SQL `DELETE FROM audit_log WHERE ...` raises a DB error and leaves the row present
- [x] 4.3 Confirm GREEN: the migration-004 trigger (task 2.4) makes 4.1/4.2 pass via the DB, NOT via the repository — this proves the DB-level defense independently of the app layer

## 5. Impersonation auth changes (CRITICAL — explicit review before coding)

- [x] 5.1 Surface the planned cross-cutting auth edits (D3) for explicit human approval; capture baseline — run existing C-03 auth tests and record "N passing" as the safety net
- [x] 5.2 RED: `TokenService` test — `create_access_token(user, actor_id=...)` embeds `actor_id`; without it, no `actor_id` claim (backward compatible)
- [x] 5.3 GREEN: add optional `actor_id` param to `TokenService.create_access_token` (`backend/app/services/auth/token_service.py`)
- [x] 5.4 RED+GREEN: add optional `actor_id: UUID | None = None` to `CurrentUser` (`backend/app/schemas/auth.py`, keep `extra='forbid'`)
- [x] 5.5 RED: `get_current_user` test — reads `actor_id` from payload into `CurrentUser`; normal token ⇒ `actor_id is None`
- [x] 5.6 GREEN: update `get_current_user` (`backend/app/api/dependencies/auth.py`) to populate `actor_id`
- [x] 5.7 Re-run the C-03 auth safety-net suite (5.1) — MUST stay green (additive, backward compatible)

## 6. AuditLogger helper (real-actor attribution)

- [x] 6.1 RED: test attribution under a NORMAL session — `actor_id` = session user, `impersonado_id` = None
- [x] 6.2 RED: test attribution under an IMPERSONATION session (`CurrentUser.actor_id` set) — `actor_id` = real actor, `impersonado_id` = `sub` (impersonated user)
- [x] 6.3 GREEN: create `backend/app/services/audit/audit_logger.py` with `log(...)` that derives attribution from `CurrentUser`, reads `ip`/`user_agent` from `Request`, persists via `AuditLogRepository` (D4)
- [x] 6.4 TRIANGULATE: test `accion`, `detalle` (JSON), `filas_afectadas` are persisted as given; `materia_id` defaults to None

## 7. Impersonation endpoints

- [x] 7.1 RED: `POST /api/v1/auth/impersonate/{user_id}` — authorized same-tenant target ⇒ token with `sub`=target, `actor_id`=real user; writes `IMPERSONACION_INICIAR` (actor=real, impersonado=target)
- [x] 7.2 RED: caller without `impersonacion:usar` ⇒ 403, no token, no audit record (fail-closed, Reglas Duras #10)
- [x] 7.3 RED: cross-tenant target ⇒ rejected, no token issued (Reglas Duras #9)
- [x] 7.4 RED: `POST /api/v1/auth/impersonate/end` with a token bearing `actor_id` ⇒ new normal token for the real actor (no `actor_id`); writes `IMPERSONACION_FINALIZAR`
- [x] 7.5 RED: `impersonate/end` on a token WITHOUT `actor_id` ⇒ rejected
- [x] 7.6 GREEN: add `backend/app/schemas/impersonation.py` (request/response, `extra='forbid'`) and the two endpoints in `backend/app/api/v1/routers/auth.py`, gated by `require_permission(Perm.IMPERSONACION_USAR)`, wiring `AuditLogger` (D3)
- [x] 7.7 TRIANGULATE: test that an arbitrary "act-as" param/header on a NORMAL request is ignored — identity stays from the verified JWT (Reglas Duras #8)

## 8. Verification & wrap-up

- [x] 8.1 Run the full backend suite; confirm coverage ≥80% lines / ≥90% on the audit + impersonation business rules
- [x] 8.2 Confirm each artifact file is ≤500 LOC; split if needed
- [x] 8.3 Mark `C-05` done in `CHANGES.md`
