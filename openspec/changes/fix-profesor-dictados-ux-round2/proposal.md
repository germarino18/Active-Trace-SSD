## Why

Round 1 of the PROFESOR dictado UX shipped, but real usage surfaced six follow-up defects and gaps. The most damaging is a silent data-integrity illusion: removing an alumno returns `204 No Content` yet the alumno never disappears from any list — because the padrón READ path skips the soft-delete filter, so soft-deleted rows keep surfacing everywhere (alumnos, actividades, atrasados). The rest are UX/parity gaps: no per-row individual comunicado in the per-dictado atrasados tab, an actividad "modal" that is actually an inline panel trapped in the tab scroll with no edit support, profesor metrics wrongly baked into the generic `/dashboard`, and a seed dictado ("Bases de Datos") still using the legacy calificación string format. These block professors from trusting the padrón and from operating dictados day-to-day, so they are addressed together as round 2.

## What Changes

- **FIX (data integrity, root cause)**: `EntradaPadronRepository.find_by_version()` and `count_by_version()` apply tenant scope but NOT the soft-delete filter that `BaseRepository.find_by_id`/`find_all` use. Add `_apply_soft_delete_filter` to both so soft-deleted padrón entries stop appearing in the alumnos list, actividades, count and atrasados views. Calificaciones persist by design (soft delete is correct) — the bug is only that bajas keep being listed. Covered by a regression integration test against a real/ephemeral DB.
- **ADD per-row individual comunicado in the per-dictado atrasados tab** (`AtrasadosDictadoPage`), reusing the already-approved flexible pipeline (`useMutationComunicadoFlexible` → `prepare_comunicado_flexible` → `enqueue_masivo`). No new send logic; the approval gate is never bypassed.
- **FIX actividad modal + ADD edit**: replace the inline actividad panel with a real overlay modal (portal to `document.body`, `fixed inset-0`, backdrop, z-index) reused for create AND a new edit form that PATCHes `fecha_limite`; editing invalidates BOTH the actividades query AND the atrasados query (a date change shifts who is atrasado).
- **MOVE profesor metrics to a dedicated `/profesor-dashboard` route**: new `ProfesorMetricsDashboardPage` holds the live professor stats currently embedded in `/dashboard`; `/dashboard` reverts to the generic static `ROLE_CONFIG` (no `useProfesorDashboard` call); navbar entry + redirect so professors land on the new route.
- **FIX seed**: the "Bases de Datos" dictado in `seed_dev.py` SHALL create proper `actividad` rows and link its calificaciones via `actividad_id`, mirroring the "Programación I" dictado's new format instead of the legacy `actividad` string.

## Capabilities

### New Capabilities
- `profesor-metrics-dashboard`: a dedicated `/profesor-dashboard` route that owns the live PROFESOR metrics, decoupled from the generic `/dashboard`.

### Modified Capabilities
- `profesor-dictado-ux`: per-row individual comunicado in the per-dictado atrasados tab; actividad overlay modal with edit-fecha-límite and dual (actividades + atrasados) cache invalidation.
- `padron-soft-delete-read`: padrón read paths SHALL exclude soft-deleted entries (alumnos list, count, actividades, atrasados).
- `seed-dev-data`: the "Bases de Datos" dictado SHALL use the actividad-row + `actividad_id` calificación format.

## Impact

- **Backend**: `app/repositories/entrada_padron_repository.py` (soft-delete filter on two methods, regression test); `seed_dev.py` (actividad rows + `actividad_id` for dictado2). No endpoint, service, schema or migration changes — actividad CRUD and the baja endpoints already exist and work.
- **Frontend**: `features/profesor/pages/AtrasadosDictadoPage.tsx` (per-row comunicado, reusing flexible form); `features/profesor/pages/ActividadesDictadoPage.tsx` (portal modal + edit form + dual invalidation, factored into sub-components to stay <200 LOC); new `ProfesorMetricsDashboardPage`; `pages/DashboardPage.tsx` (revert to static config); `App.tsx` (new route + redirect); `features/layout/components/AppLayout.tsx` (nav entry).
- **Governance**: comunicación is CRÍTICO, but item 2 only adds a new entry point onto the already-approved enqueue/approval pipeline — no gate bypass. Items 1 and 6 are backend (root-cause fix + seed, BAJO/MEDIO). Items 3/4/5 are frontend pages (BAJO). No auth, RBAC, tenancy, or migration changes.
