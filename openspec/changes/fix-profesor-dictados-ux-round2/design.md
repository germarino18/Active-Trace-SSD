## Context

This is round 2 of the PROFESOR dictado UX work; round 1 (`fix-profesor-dictados-ux`) already moved the views under `/dictados`, added per-row baja, inline registrar-nota, and dictado-name rendering. Six follow-up items were traced end-to-end during `/opsx:explore`:

1. **DELETE alumno returns 204 but the alumno never disappears.** Root cause confirmed at the READ side. `backend/app/repositories/entrada_padron_repository.py`:
   - `find_by_version()` (lines 28-34) and `count_by_version()` (lines 36-42) apply `_apply_tenant_scope(query)` but NOT `_apply_soft_delete_filter(query)`.
   - `BaseRepository` (`backend/app/repositories/base.py`) defines `_apply_soft_delete_filter` (line 38; adds `WHERE deleted_at IS NULL` when the model has `deleted_at` and `_include_soft_deleted` is false). `find_by_id` (line 59) and `find_all` (line 66) both apply it; the two custom `*_by_version` methods skip it.
   - The baja WRITE side is correct: `POST .../padron/alumnos/bulk-baja` and `DELETE .../padron/alumnos/{entrada_padron_id}` in `backend/app/api/v1/routers/profesor.py` delegate to `ProfesorService.baja_alumnos_bulk` / `baja_alumno_dictado` which set `entrada.deleted_at` and commit.
   - Every padrón read funnels through `find_by_version` (`obtener_padron_activo` → alumnos list; `get_alumnos_clasificados` → actividades; `get_atrasados_cross_materia` → atrasados), so soft-deleted entries persist across all three views.

2. **No per-row individual comunicado in the per-dictado atrasados tab.** The flexible individual/general comunicado already shipped lives in `frontend/src/features/academico/pages/AtrasadosGeneralPage.tsx` (cross-materia) via `ComunicadoFlexibleForm` + `useMutationComunicadoFlexible`. The per-dictado tab `frontend/src/features/profesor/pages/AtrasadosDictadoPage.tsx` only has per-subtipo general buttons.

3 + 5. **Actividad "modal" trapped in scroll + no edit of `fecha_limite`.** Backend CRUD already exists: `backend/app/api/v1/routers/actividades.py` (`POST /api/v1/actividades/dictados/{dictado_id}`, `PATCH /api/v1/actividades/{actividad_id}`, `DELETE /api/v1/actividades/{actividad_id}`), service `backend/app/services/actividad_service.py`. The frontend `CrearActividadModal` (~line 117 of `ActividadesDictadoPage.tsx`) is an inline `<div className="rounded-xl border…">`, not an overlay, and each activity card is `overflow-hidden`, so the panel is trapped in the tab scroll. There is no edit UI.

4. **Profesor metrics baked into the generic `/dashboard`.** `frontend/src/pages/DashboardPage.tsx` calls `useProfesorDashboard(primaryRole === 'PROFESOR')` and swaps live stats in. The user confirmed this should move to a new `/profesor-dashboard` route, and `/dashboard` should revert to the generic static `ROLE_CONFIG`.

6. **Seed legacy format.** `backend/seed_dev.py` dictado2 ("Bases de Datos") inserts calificaciones with the `actividad` STRING only — no `actividad` rows, no `actividad_id` — while dictado1 ("Programación I") uses the new `actividad`-row + `actividad_id` format.

Constraints: project hard rules apply — Routers→Services→Repositories→Models, soft-delete only, row-level multi-tenancy, RBAC fail-closed, identity from JWT session, Pydantic `extra='forbid'`, backend files ≤500 LOC, React components <200 LOC, no `any`, TanStack Query for all fetches, NO DB mocks in tests (real/ephemeral DB), coverage ≥80% lines / ≥90% business rules.

## Goals / Non-Goals

**Goals:**
- Soft-deleted padrón entries STOP appearing in the alumnos list, count, actividades, and atrasados views (single root-cause fix in the repository read methods), proven by a regression integration test.
- Per-row "Comunicado individual" in the per-dictado atrasados tab, reusing the approved flexible pipeline.
- A real overlay modal for actividades (create + new edit-`fecha_limite` form) that floats above the list, with edit invalidating BOTH the actividades and atrasados queries.
- Profesor live metrics live at a dedicated `/profesor-dashboard`; `/dashboard` reverts to generic static config.
- The "Bases de Datos" seed dictado uses the actividad-row + `actividad_id` format.

**Non-Goals:**
- No new backend endpoints, services, schemas, or migrations. Actividad CRUD and the baja endpoints already exist.
- No change to soft-delete semantics for calificaciones (they persist by design — correct).
- No new send/approval logic for comunicados; the approval gate is unchanged.
- No redesign of the `/dictados` routes or the round-1 views.
- No multi-cohorte support (a dictado remains exactly one cohorte).

## Decisions

### D1 — Fix the soft-delete leak at the repository read methods, not at the service or query call sites
Add `query = self._apply_soft_delete_filter(query)` after `_apply_tenant_scope(query)` in BOTH `find_by_version()` and `count_by_version()`. This mirrors exactly what `find_by_id`/`find_all` already do and fixes all three leaking views (alumnos, actividades, atrasados) at the single funnel point.
- **Alternative considered**: filter `deleted_at IS NULL` in each service method (`obtener_padron_activo`, `get_alumnos_clasificados`, `get_atrasados_cross_materia`). Rejected — scatters the invariant across N call sites, violates "repositories own scoping", and would drift.
- **Regression test** (integration, real/ephemeral DB, NO DB mocks): seed a dictado + padrón, baja one entry (set `deleted_at`), then assert the entry is absent from `find_by_version`, that `count_by_version` decremented, and that it is gone from the atrasados read path. RED must fail against the current code (entry still present) before the one-line fix turns it GREEN. The SAFETY NET is the existing repository test suite run before touching the file.

### D2 — Reuse the flexible comunicado pipeline for the per-row individual comunicado
The per-row button in `AtrasadosDictadoPage` opens the SAME `ComunicadoFlexibleForm` already used by `AtrasadosGeneralPage`, pre-scoped to the single alumno+atraso row, and submits through `useMutationComunicadoFlexible` → backend `prepare_comunicado_flexible` → `enqueue_masivo`.
- **Rationale / governance**: comunicación is CRÍTICO, but this adds only a new ENTRY POINT onto the already-approved enqueue/approval pipeline. No bypass of the approval gate, no new send path. This is the minimal, lowest-risk way to reach parity with the cross-materia view.
- **Alternative considered**: a bespoke single-recipient send endpoint. Rejected — duplicates approved logic and creates a second path that could skip the gate.

### D3 — Real overlay modal via portal, shared by create and edit; edit invalidates two queries
Extract a real modal component (React portal to `document.body`, `fixed inset-0`, semi-opaque backdrop, elevated z-index) so it floats above the `overflow-hidden` activity cards. The same modal hosts the existing create form AND a new edit form bound to an actividad's `fecha_limite` (nullable Date). Editing calls `PATCH /api/v1/actividades/{actividad_id}` and on success invalidates BOTH `['profesor','actividades',dictadoId]` (or the existing actividades query key) AND the atrasados query key(s) — because changing `fecha_limite` re-partitions who is atrasado.
- **Invalidation graph** (edit + create + delete of an actividad):
  - actividades query → list must reflect the changed/added/removed row
  - per-dictado atrasados query (`['profesor','atrasados',dictadoId]`) → recompute atraso membership
  - cross-materia atrasados query (`['profesor','atrasados-general']`) → recompute, since the actividad belongs to a dictado the professor also sees there
- **Component budget**: `ActividadesDictadoPage.tsx` is already ~533 LOC. Factor out the modal, the create form, and the edit form into separate sub-components so each file stays <200 LOC. Forms use React Hook Form + Zod; the aprobado/styled controls use the design-system `Button`/inputs from `@/shared/components/ds`.
- **Alternative considered**: keep the inline panel but lift it out of the `overflow-hidden` card with CSS. Rejected — the user explicitly wants a floating modal above the list, and a portal is the robust, conventional approach.

### D4 — Split the dashboard: dedicated `/profesor-dashboard`, revert `/dashboard` to static
Create `ProfesorMetricsDashboardPage` holding the live metrics block (Materias asignadas, Alumnos en riesgo, Encuentros) currently embedded in `DashboardPage` via `useProfesorDashboard`. Register it at `/profesor-dashboard` in `App.tsx`, add an `AppLayout` nav entry, and add a redirect so a PROFESOR lands there. `DashboardPage` reverts to the generic static `ROLE_CONFIG` and stops calling `useProfesorDashboard`.
- **What moves**: the `useProfesorDashboard(...)` call and the professor StatCards/metrics block.
- **What stays**: `/dashboard` keeps rendering generic static `ROLE_CONFIG` for all roles; `/dictados` and `/dictados/:dictadoId` and their tabs are untouched.
- **Alternative considered**: a feature flag inside `/dashboard`. Rejected — the user wants a clean separation and a stable generic dashboard.

### D5 — Seed parity for "Bases de Datos"
In `seed_dev.py`, create `actividad` rows for dictado2 mirroring dictado1's block and link its calificaciones via `actividad_id` instead of the `actividad` string. BAJO governance; data-only.

## Risks / Trade-offs

- **[Soft-delete fix changes existing read results]** → Mitigation: that is the intended behavior; the regression test plus the SAFETY-NET run of the existing repository suite guard against breaking the non-deleted read paths. Calificación persistence is unaffected (different table/path).
- **[Comunicado entry point could be mistaken for a new send path]** → Mitigation: reuse `useMutationComunicadoFlexible` verbatim; no new mutation, no new endpoint; the approval gate stays the single chokepoint. Add a frontend test asserting the per-row button calls the existing flexible mutation.
- **[Modal portal regressions / focus-trap / z-index]** → Mitigation: portal to `document.body`, `fixed inset-0` backdrop; RTL tests assert the modal renders outside the card subtree (above the list) and closes on backdrop/escape.
- **[Missed atrasados invalidation on actividad edit]** → Mitigation: explicit dual-invalidation requirement + a test that asserts both query keys are invalidated after a `fecha_limite` edit.
- **[Dashboard split breaks deep links / role redirect]** → Mitigation: keep `/dashboard` working for every role; add a test for the PROFESOR redirect to `/profesor-dashboard` and for `/dashboard` rendering generic static config without calling `useProfesorDashboard`.
- **[`ActividadesDictadoPage` exceeding 200 LOC]** → Mitigation: extract modal + create form + edit form into sub-components; verify each file size.

## Migration Plan

No schema/migration. Deploy order is irrelevant across items (independent). Recommended apply order for testability: (1) backend soft-delete fix + regression test, (6) seed parity, then frontend items (2), (3/5), (4). Rollback: revert the change; no data migration to undo. Seed change only affects `seed_dev.py` (dev data).

## Open Questions

- None blocking. The exact existing TanStack query keys for actividades/atrasados will be read from the codebase during apply and matched verbatim; the spec states the invalidation contract, the apply step binds the literal keys.
