# Tasks — fix-profesor-dictados-ux-round2

Strict TDD for every task: SAFETY NET (run existing tests for any file you will modify; capture baseline; a pre-existing failure is reported, never fixed here) → RED (write the failing test first) → GREEN (minimum code to pass) → TRIANGULATE (≥2 cases: happy path + edge) → REFACTOR (tests green after each step). NO DB mocks on the backend — use a real/ephemeral test DB. Coverage ≥80% lines, ≥90% business rules. Conventional Commits, no Co-Authored-By.

Recommended order: backend root-cause (group 1) and seed parity (group 2) first (independently testable), then the frontend items (groups 3–5).

## 1. Backend — padrón soft-delete read fix (root cause)

- [x] 1.1 SAFETY NET: run the existing repository test suite covering `EntradaPadronRepository`; record baseline (e.g. "N passing"). Load skills `test-driven-development`, `python-testing-patterns`, `async-python-patterns`. — baseline 70 green (57 padron + 13 profesor).
- [x] 1.2 RED: write a regression integration test (real/ephemeral DB, NO mocks) that seeds a dictado + padrón version, soft-deletes one entry (`deleted_at`), and asserts `find_by_version` does NOT return it. Must FAIL against current code.
- [x] 1.3 GREEN: add `query = self._apply_soft_delete_filter(query)` after `_apply_tenant_scope` in `EntradaPadronRepository.find_by_version()` (`backend/app/repositories/entrada_padron_repository.py`). Test passes. — also fixed the deeper root cause: `EntradaPadron` was missing `SoftDeleteMixin`/`deleted_at` entirely (model + migration 019).
- [x] 1.4 TRIANGULATE: add a case for `count_by_version` (asserts the count excludes the soft-deleted entry) and a tenant-isolation case (other-tenant entries never returned). Apply the same filter to `count_by_version()`; both pass.
- [x] 1.5 TRIANGULATE: add an integration case asserting a soft-deleted alumno is absent from the atrasados read path (`get_atrasados_cross_materia`) and from `get_alumnos_clasificados` (actividades), confirming the single fix covers all three views.
- [x] 1.6 REFACTOR: confirm no behavior change for active/non-deleted entries; verify `entrada_padron_repository.py` stays ≤500 LOC (53 LOC); full repository suite green.

## 2. Backend — seed parity for "Bases de Datos" dictado

- [x] 2.1 SAFETY NET: locate dictado1 (Programación I) actividad-row + `actividad_id` block in `backend/seed_dev.py` (~lines 286-360) and dictado2 (Bases de Datos) legacy string block (~lines 364-386). Run any existing seed smoke test if present. — no prior seed tests.
- [x] 2.2 RED: add/extend a test (or seed assertion) verifying that after seeding, the "Bases de Datos" dictado has `actividad` rows and every calificación is linked via `actividad_id`. Must FAIL against current seed.
- [x] 2.3 GREEN: create `actividad` rows for dictado2 mirroring dictado1's format and link its calificaciones via `actividad_id` instead of the `actividad` string. Test passes.
- [x] 2.4 TRIANGULATE + REFACTOR: assert both dictados share the actividad-row format (no calificación relying solely on the legacy string); confirm seed runs end-to-end without error. — `tests/test_seed/test_seed_parity.py` 2/2 green.

## 3. Frontend — per-row individual comunicado in per-dictado atrasados tab

- [x] 3.1 SAFETY NET: run existing tests for `frontend/src/features/profesor/pages/AtrasadosDictadoPage.tsx`; record baseline (5 passing). Load skills `react-expert`, `tanstack-query`, `react-hook-form-zod`, `typescript-advanced`, `activia-trace-design`. Read `AtrasadosGeneralPage.tsx` to reuse `ComunicadoFlexibleForm` + `useMutationComunicadoFlexible`.
- [x] 3.2 RED: write a vitest + RTL + userEvent test asserting that clicking the per-row "Comunicado individual" button opens `ComunicadoFlexibleForm` pre-scoped to that single alumno and that submit calls `useMutationComunicadoFlexible` (mocked at the hook boundary). Must FAIL (no button yet).
- [x] 3.3 GREEN: add the per-row "Comunicado individual" control to `AtrasadosDictadoPage`, reusing the existing flexible form and mutation (no new send path, no gate bypass). Use design-system `Button` from `@/shared/components/ds`. Test passes.
- [x] 3.4 TRIANGULATE: add a case asserting the approval gate is preserved (the per-row submit invokes the SAME flexible mutation, not a new one) and a case for the empty/edge row. REFACTOR to keep the component <200 LOC (169 LOC); no `any`. — CRÍTICO governance: no new send path/endpoint; reuses approved pipeline.

## 4. Frontend — actividad overlay modal (create + edit fecha_limite) with dual invalidation

- [x] 4.1 SAFETY NET: run existing tests for `frontend/src/features/profesor/pages/ActividadesDictadoPage.tsx`; record baseline (7 passing). Load skills `react-expert`, `tanstack-query`, `react-hook-form-zod`, `tailwind-design-system`, `activia-trace-design`. Read existing actividades/atrasados query keys to bind invalidation literally.
- [x] 4.2 RED: write an RTL test asserting the actividad modal renders via a portal OUTSIDE the activity-card subtree (above the list) with a `fixed inset-0` backdrop, and closes on backdrop/escape. Must FAIL (current panel is inline).
- [x] 4.3 GREEN: extract a real overlay modal component (`ActividadOverlayModal`, portal to `document.body`, `fixed inset-0`, backdrop, Escape-close) and host the existing create form inside it. Test passes.
- [x] 4.4 RED: write a test for the new edit form — editing `fecha_limite` calls `PATCH /api/v1/actividades/{actividad_id}` with the new date (mocked at the service/hook boundary). Must FAIL (no edit UI).
- [x] 4.5 GREEN: add the edit form (`EditarActividadForm`, React Hook Form + Zod, nullable date) wired to the existing PATCH endpoint via new `useMutationEditarActividad`. Test passes.
- [x] 4.6 RED: write a test asserting that on a successful actividad edit (and create/delete) the mutation invalidates BOTH the actividades query for the dictado AND the atrasados queries. Must FAIL. — actual keys bound: `['profesor','actividades',dictadoId]`, `['profesor','atrasados',dictadoId]`, `['profesor','atrasados-general']`.
- [x] 4.7 GREEN: add the dual invalidation in the create/edit/delete mutation success handlers. Test passes.
- [x] 4.8 TRIANGULATE + REFACTOR: cover the create path and the delete path for the dual invalidation; ensure aprobado/controls use design-system components; factor modal + create form + edit form into sub-components so each file stays <200 LOC; no `any`. — page 113 LOC; modal 49, create 121, edit 79. NOTE deviation: `ActividadCard.tsx` multi-component file is 278 LOC (no single component >~100 LOC) — flagged for optional split.

## 5. Frontend — split dashboard: dedicated /profesor-dashboard, revert /dashboard to static

- [x] 5.1 SAFETY NET: run existing tests for `frontend/src/pages/DashboardPage.tsx`, `App.tsx`, and `AppLayout.tsx`; record baseline (11/11). Load skills `react-expert`, `tanstack-query`, `activia-trace-design`.
- [x] 5.2 RED: write a test asserting `/profesor-dashboard` renders a new `ProfesorMetricsDashboardPage` that calls `useProfesorDashboard` and shows the live metrics. Must FAIL (route/page do not exist).
- [x] 5.3 GREEN: create `ProfesorMetricsDashboardPage` holding the live metrics block; register `/profesor-dashboard` in `App.tsx`. Test passes.
- [x] 5.4 RED: write a test asserting `/dashboard` renders the generic static `ROLE_CONFIG` for a PROFESOR and does NOT call `useProfesorDashboard`. Must FAIL (currently embeds professor metrics).
- [x] 5.5 GREEN: revert `DashboardPage` to the generic static `ROLE_CONFIG` (remove the `useProfesorDashboard` call and professor StatCards). Test passes.
- [x] 5.6 TRIANGULATE: add a navbar-entry test (`AppLayout` links to `/profesor-dashboard`) and a PROFESOR-redirect test. Add an existing-routes-untouched assertion for `/dictados` and `/dictados/:dictadoId`. — navbar entry "Mis Métricas" → `/profesor-dashboard`.
- [x] 5.7 REFACTOR: keep `ProfesorMetricsDashboardPage` <200 LOC (88 LOC); no `any`; confirm `/dashboard` and `/dictados` regressions all green.

## 6. Verification

- [x] 6.1 Run the full backend test suite (real/ephemeral DB) and the full frontend vitest suite; all green, no pre-existing failures reintroduced. — **Frontend 498/498 green.** Backend, our scope on the 5434 test DB: **325 passed / 0 failed** (soft-delete regression, seed parity, profesor batch2, analisis, calificaciones). Two PRE-EXISTING issues, NOT introduced here: (a) ~921 errors + 3 "failures" are `InvalidPasswordError` on `localhost:5432` for dirs without a 5434 override (env limitation); (b) 9 `test_comunicado_flexible` errors from a missing `auth_user` fixture committed in the prior change `comunicado-profesor-individual-general` (never run; belongs to that change's task 6.1).
- [~] 6.2 Confirm coverage thresholds (≥80% lines, ≥90% business rules) for the touched modules. — DEFERRED: full-suite coverage not measurable in this env (root-conftest dirs can't connect to 5432). Touched-module tests pass; precise coverage % pending a fully-provisioned DB.
- [x] 6.3 Mark every task `[x]`, note any deviations, and produce the TDD Cycle Evidence table for the apply summary.

## 7. Review-round fixes (post-apply feedback)

### 7a. Backend — tareas propias del profesor (CRUD completo, RBAC owner-only)
- [x] 7a.1 SAFETY NET: run existing `tests/test_tareas`; baseline 49/49. Confirmed `POST /tareas/mias` / `PATCH /tareas/mias/{id}` did NOT exist; `TareaCreatePropia` was unused.
- [x] 7a.2 RED+GREEN: `POST /api/v1/tareas/mias` — profesor creates own tarea (asignado_a/asignado_por = current_user from session), gate `require_permission(Perm.TAREAS_GESTIONAR)`, body `TareaCreatePropia` (`extra='forbid'`). Identity from session, never from body.
- [x] 7a.3 RED+GREEN: `PATCH /api/v1/tareas/mias/{tarea_id}` — edit own tarea (`descripcion?`, `materia_id?`, `estado?` via new `TareaUpdatePropia`); OWNER-ONLY: 404 (no existence leak) if not owned; tenant-scoped via `find_own_tarea`.
- [x] 7a.4 TRIANGULATE: owner isolation (other profesor → 404), tenant isolation, `extra='forbid'` → 422, estado-only update. Service in `tareas_service.py`; no business logic in router; all files ≤500 LOC. — 63/63 green.

### 7b. Frontend — tareas view: crear + editar (modal/portal), fix dropdown atrapado
- [x] 7b.1 SAFETY NET: baseline `MisTareasProfesorPage` 5/5.
- [x] 7b.2 RED+GREEN: "Crear tarea" button opens a portal overlay modal (reuses `ActividadOverlayModal`, NOT clipped); RHF+Zod (descripcion + materia opcional) → `crearTareaPropia`/`useMutationCrearTareaPropia` (`POST /tareas/mias`); invalidates `['profesor','tareas','mias']`.
- [x] 7b.3 RED+GREEN: per-row "Editar" button opens a portal edit modal (estado + descripción/otros datos) → `editarTareaPropia`/`useMutationEditarTareaPropia` (`PATCH /tareas/mias/{id}`); replaced the clipped `position:absolute` estado dropdown. Invalidates on success.
- [x] 7b.4 TRIANGULATE + REFACTOR: create vs edit + validation edge cases; `CrearTareaModal` ≈90 LOC, `EditarTareaModal` ≈115 LOC, page ≈115 LOC; no `any`; design-system `Button`. — full FE suite 535/535.

### 7c. Frontend — actividad: fecha de cierre junto al tipo + indicador próxima/vencida
- [x] 7c.1 RED+GREEN: `ActividadCard` renders `fecha_limite` inline right after `(tipo)`; pure helper `getFechaLimiteStatus` → badge **Vencida** (< hoy) / **Próxima** (≤7 días) / none. New `utils/fechaLimiteStatus.ts`.
- [x] 7c.2 TRIANGULATE: vencida, próxima (hoy / 7d / boundary), lejana, sin fecha; no `any`.

### 7d. Frontend — profesor no accede a /dashboard (solo /profesor-dashboard)
- [x] 7d.1 RED+GREEN: new `DashboardEntry` (role from session) — PROFESOR → `<Navigate to="/profesor-dashboard">`; other roles render `DashboardPage`. `/dashboard` route now uses `DashboardEntry`.
- [x] 7d.2 RED+GREEN: `buildSectionsForRole` hides the generic "Dashboard → /dashboard" item for PROFESOR (keeps "Mis Métricas"); other roles still see it.
- [x] 7d.3 TRIANGULATE: PROFESOR redirected; ADMIN/ALUMNO/TUTOR unaffected; `/dictados` + `/profesor-dashboard` untouched. — round2 dir 35/35.

### 7e. Verify #1 (actividad edit modal): CONFIRMED already portaled (`ActividadOverlayModal` → `createPortal(document.body)`, `fixed inset-0 z-50`); no `transform`/`filter`/`container-type` on `#root`/`body`. The genuinely-clipped element was the tareas estado dropdown — fixed in 7b. Pending user confirmation against a fresh build.

## Deviations / notes
- **Deeper root cause than proposed (D1+):** `EntradaPadron` lacked `SoftDeleteMixin`/`deleted_at` entirely — the service set `deleted_at` on a non-existent column. Fix required adding the mixin to the model + Alembic migration `019_add_deleted_at_to_entrada_padron.py` (one migration per schema change) in addition to the `_apply_soft_delete_filter` calls. CRÍTICO domain (core-models/migration) — surfaced here for review.
- `ActividadCard.tsx` is a 278-LOC multi-component file (no single component >~100 LOC) — optional further split.
- Pre-existing `auth_user` fixture gap blocks the prior change's flexible-pipeline backend tests; recommend fixing as part of closing `comunicado-profesor-individual-general` task 6.1.
- Nothing committed (awaiting explicit user request).
