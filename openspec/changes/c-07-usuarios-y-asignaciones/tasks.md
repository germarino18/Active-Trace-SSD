# Tasks — C-07 usuarios-y-asignaciones

> Strict TDD: every implementation task is RED → GREEN → TRIANGULATE → REFACTOR.
> Real Postgres test DB, no DB mocks (Reglas Duras #4/#16). CRITICAL governance
> (auth/RBAC/core-models): the auth-touching tasks (group 6) require explicit human
> review before writing code, and the C-03/C-04 auth safety net (216 tests) must
> stay green throughout. Flow Routers→Services→Repositories→Models (Regla Dura #11).

## 1. Encryption infrastructure (EncryptedString)

- [x] 1.1 RED: test that `EncryptedString` bind→result round-trips a plaintext (encrypt on write, decrypt on read) using the existing `encrypt_value`/`decrypt_value` primitives and `get_encryption_key()`
- [x] 1.2 RED: test that the value stored at the DB layer (the bound param) is NOT the plaintext (ciphertext at rest)
- [x] 1.3 GREEN: create `backend/app/core/crypto.py` with `EncryptedString(TypeDecorator)` wrapping `app/core/security.py` (impl = String/Text, base64 of nonce+ciphertext)
- [x] 1.4 TRIANGULATE: test None/empty handling and that two encryptions of the same plaintext differ (random nonce) yet both decrypt correctly

## 2. Usuario model & registration

- [x] 2.1 RED: model test — `Usuario` has `user_id` (FK→users.id, unique), `nombre`, `apellidos`, encrypted `dni`/`cuil`/`cbu`/`alias_cbu`, `banco`, `regional`, `legajo`, `legajo_profesional` (nullable), `facturador` (bool), `estado` (Activo|Inactivo); uses BaseMixin+TenantMixin+SoftDeleteMixin+AuditMixin; has NO `email` column (D1)
- [x] 2.2 GREEN: create `backend/app/models/usuario.py` and register it in `backend/app/models/__init__.py`
- [x] 2.3 TRIANGULATE: test that `dni`/`cuil`/`cbu`/`alias_cbu` use `EncryptedString` (ciphertext at rest, plaintext via ORM) and that the partial unique index `(tenant_id, user_id)` over alive rows rejects a duplicate profile

## 3. Asignacion model & registration

- [x] 3.1 RED: model test — `Asignacion` has `usuario_id` (FK→usuario), `rol`, nullable context `dictado_id`/`materia_id`/`carrera_id`/`cohorte_id`, `comisiones` (ARRAY), `responsable_id` (FK→usuario, nullable), `desde`/`hasta` (date, hasta nullable); uses BaseMixin+TenantMixin+SoftDeleteMixin+AuditMixin; has NO `estado_vigencia` column (D3, derived)
- [x] 3.2 GREEN: create `backend/app/models/asignacion.py` and register it in `backend/app/models/__init__.py`
- [x] 3.3 TRIANGULATE: test that `rol = NEXO` persists and that all-NULL context (tenant-global) and partial context both persist

## 4. Migration 007 (tables, indexes, seed, backfill)

- [x] 4.1 Write `backend/alembic/versions/007_create_usuario_asignacion.py` with `revision = "a7b8c9d0e1f2"`, `down_revision = "f6a7b8c9d0e1"` (D4): `create_table("usuario", ...)` + partial unique index `(tenant_id, user_id)` over alive rows
- [x] 4.2 In migration 007 `upgrade()`: `create_table("asignacion", ...)` + indexes `(tenant_id, usuario_id)` and `(tenant_id, rol)`
- [x] 4.3 In migration 007 `upgrade()`: seed `equipos:asignar` permission (module `equipos`) per alive tenant, and `rol_permiso` for COORDINADOR and ADMIN (es_propio=False), replicating the migration-003 seed loop with `ON CONFLICT DO NOTHING` (D4/D5)
- [x] 4.4 In migration 007 `upgrade()`: backfill — for each alive `users` and each `users.roles[i]`, create a minimal `usuario` shell (if absent) and an `asignacion` with that `rol`, NULL context, `desde = users.created_at::date`, `hasta = NULL`; idempotent via unique indexes
- [x] 4.5 In migration 007 `downgrade()`: drop `equipos:asignar` rol_permiso → permiso seed, then `asignacion`, then `usuario` (D4)
- [x] 4.6 Test migration up/down applies cleanly against the test DB (tables + seed created, then fully removed); `users.roles` is left intact

## 5. Permission constant & repository for role resolution

- [x] 5.1 RED+GREEN: test and add `Perm.EQUIPOS_ASIGNAR = "equipos:asignar"` to `backend/app/core/permissions.py`
- [x] 5.2 RED: test `AsignacionRepository.find_roles_vigentes(tenant_id, usuario_id)` returns DISTINCT `rol` of alive Vigente asignaciones (desde<=hoy AND (hasta IS NULL OR hoy<=hasta)), tenant-scoped
- [x] 5.3 GREEN: create `backend/app/repositories/asignacion_repository.py` extending `BaseRepository[Asignacion]` with CRUD + `find_roles_vigentes`
- [x] 5.4 TRIANGULATE: test that a Vencida asignacion (hasta in the past) is excluded, a future-dated one (desde in the future) is excluded, and a multi-rol user returns all distinct vigente roles

## 6. Roles source change (CRITICAL — explicit review before coding)

- [x] 6.1 Surface the planned cross-cutting auth edits (D3) for explicit human approval; capture baseline — run the C-03/C-04 auth+RBAC suite and record "N passing" as the safety net
  - Baseline captured: full backend suite = 238 passed (run at start of Group 6, before any auth edits). CRITICAL gate approved by explicit user decision (engram `opsx/c-07-usuarios-y-asignaciones/design-decisions` #24): test factory seeds Usuario+Asignacion per role (mirrors migration 007 backfill), no fallback to `users.roles`.
- [x] 6.2 RED: `TokenService` test — the `roles` claim is derived from the user's Vigente asignaciones, NOT from `users.roles`; a user with a Vencida-only PROFESOR asignacion gets no PROFESOR in the claim
  - `backend/tests/test_auth/test_token_service.py`: added `test_create_access_token_roles_come_from_vigente_asignaciones`, `test_create_access_token_excludes_vencida_asignacion_role`, `test_create_access_token_user_without_usuario_has_empty_roles`, `test_create_access_token_multirol_returns_distinct_sorted_roles`.
- [x] 6.3 GREEN: update `TokenService.create_access_token` (`backend/app/services/auth/token_service.py`) to source `roles` from `AsignacionRepository.find_roles_vigentes` instead of `user.roles` (keep the `actor_id` impersonation behavior intact)
  - `create_access_token` is now `async def create_access_token(self, user, db, actor_id=None)`. Looks up `Usuario` via new `UsuarioRepository.find_by_user_id(tenant_id, user_id)` (`backend/app/repositories/usuario_repository.py`); if found, `roles = sorted(AsignacionRepository.find_roles_vigentes(...))`, else `roles = []` (fail-closed, no fallback to `user.roles`).
  - Updated all 5 call sites in `backend/app/api/v1/routers/auth.py` (authenticate, login, refresh, impersonate_end, impersonate) to `await ts.create_access_token(user_or_actor_or_target, db, ...)`.
- [x] 6.4 RED+GREEN: confirm `get_current_user` (`backend/app/api/dependencies/auth.py`) still reads `roles` from the verified JWT into `CurrentUser.roles` (now already-derived); add a test asserting `require_permission` resolves against those roles
  - No code change needed (already reads `payload.get("roles", [])` into `CurrentUser.roles`). Existing `tests/test_permissions/test_permission_system.py` and `tests/test_auth/test_get_current_user.py` already cover `require_permission` resolving against `CurrentUser.roles`.
- [x] 6.5 Re-run the safety net (6.1) — MUST stay green; the backfill guarantees existing users keep equivalent effective roles
  - Full backend suite: 242/242 passed (238 baseline + 4 new TokenService tests). Test-factory fix: `backend/tests/helpers.py` adds `seed_asignaciones_for_user(db_session, user, roles)` (mirrors migration 007 backfill shape: Usuario shell + Asignacion per role, NULL context, `desde=today()`, `hasta=NULL`). Wired into `_make_user`/fixtures in `tests/test_permissions/conftest.py` and `tests/test_impersonation/conftest.py`.
  - Deviation: the ~216 pre-existing auth/RBAC tests pass via `make_token()` helpers that manually craft JWTs from `user.roles` (bypassing `create_access_token` entirely) — these were never at risk from the roles-source change. The factory fix was still applied to `admin_user`/`profesor_user`/`alumno_user`/`_make_user` fixtures per the approved decision, so any future test exercising `create_access_token`/`find_roles_vigentes` on these fixtures gets realistic Asignacion data.

## 7. Usuario ABM endpoints

- [x] 7.1 RED: `POST/GET/PATCH/DELETE /api/admin/usuarios` happy paths — create/read/update/soft-delete a `usuario` tenant-scoped, gated by `usuarios:gestionar`
- [x] 7.2 RED: caller without `usuarios:gestionar` ⇒ 403, no change (fail-closed, Regla Dura #10)
- [x] 7.3 RED: PII (`dni`/`cuil`/`cbu`/`alias_cbu`) is NOT present in the default list/read response schema, and is ciphertext at rest (Regla Dura #12)
- [x] 7.4 RED: a `legajo` supplied as an identity selector is ignored — identity stays the verified-JWT UUID (Reglas Duras #8/#14)
- [x] 7.5 GREEN: add `backend/app/schemas/usuario.py` (request/response, `extra='forbid'`), `backend/app/services/usuario_service.py`, `backend/app/repositories/usuario_repository.py`, and the router in `backend/app/api/v1/routers/usuarios.py` gated by `require_permission(Perm.USUARIOS_GESTIONAR)`
- [x] 7.6 TRIANGULATE: cross-tenant access is rejected; soft-delete marks `deleted_at` and the row remains (Reglas Duras #9/#13)

## 8. Asignacion CRUD endpoints

- [x] 8.1 RED: `POST/GET/PATCH/DELETE /api/asignaciones` happy paths — create/read/update/soft-delete tenant-scoped, gated by `equipos:asignar`
- [x] 8.2 RED: caller without `equipos:asignar` ⇒ 403, no change (fail-closed)
- [x] 8.3 RED: derived `estado_vigencia` is exposed in responses (Vigente|Vencida) computed from dates, never stored
- [x] 8.4 RED: a Vencida asignacion is retained and does NOT contribute to effective roles (KB E5 rule)
- [x] 8.5 RED: `responsable_id` and `comisiones` round-trip; `rol = NEXO` accepted (zero permissions)
- [x] 8.6 GREEN: add `backend/app/schemas/asignacion.py` (`extra='forbid'`), `backend/app/services/asignacion_service.py`, and the router in `backend/app/api/v1/routers/asignaciones.py` gated by `require_permission(Perm.EQUIPOS_ASIGNAR)`
- [x] 8.7 TRIANGULATE: cross-tenant rejected; context FKs (dictado/materia/carrera/cohorte) validated against the same tenant

## 9. Verification & wrap-up

- [x] 9.1 Run the full backend suite; confirm coverage ≥80% lines / ≥90% on the usuarios/asignaciones/role-resolution business rules
  - Full suite: 267 tests collected, 266 passed + 1 pre-existing flaky (timing-sensitive `test_verify_code_from_adjacent_window`, passes in isolation, unrelated to C-07). `pytest-cov`/`coverage` are not installed in this environment (pre-existing gap, no `[tool.coverage]` config in pyproject.toml) -- numeric coverage could not be measured. Qualitative check: every Scenario in `specs/usuarios/spec.md` and `specs/asignaciones/spec.md` has at least one corresponding test (groups 1-8); role-resolution (`find_roles_vigentes`, vigente/vencida, multi-rol) covered by group 5/6/8 tests.
- [x] 9.2 Confirm each artifact file is ≤500 LOC; split if needed (Regla Dura #15)
  - All C-07-authored/modified files are well under 500 LOC (largest: `alembic/versions/007_create_usuario_asignacion.py` at 222, `app/services/asignacion_service.py` at 155, `app/api/v1/routers/asignaciones.py` at 134). `app/api/v1/routers/auth.py` is 511 LOC and over the limit, but this is a PRE-EXISTING condition (511 LOC before C-07 touched it; group 6's edit was a net-zero-LOC change to 5 lines). Splitting `auth.py` is an unscoped CRITICAL-domain refactor not covered by design.md -- flagged for a future change, not done here.
- [x] 9.3 Correct CHANGES.md: C-07's migration is **007** (not 005); mark `C-07` done
  - Updated `CHANGES.md` `[C-07]` entry: `**Estado**: \`[x]\` completado`, migration corrected to 007, scope description corrected to match D1 (no `email` on `Usuario`, unicidad `(tenant_id, user_id)`) and D3 (Asignacion-vigente replaces `users.roles`, BREAKING RBAC note, `equipos:asignar` seed).
