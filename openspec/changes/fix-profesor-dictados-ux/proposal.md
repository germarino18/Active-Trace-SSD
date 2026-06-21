## Why

The PROFESOR dictado views shipped in `frontend-profesor` work but expose several UX rough edges: the dictado list/detail live under a developer-flavored `/profesor/dashboard` route, the breadcrumb and header surface raw UUIDs instead of the dictado name, the padrón only supports bulk baja (per-row delete is missing and a delete bug is reported), the "Registrar nota" modal floats at the top of the page instead of inline in the activity it targets, stat numbers and the atrasados panel go stale after mutations, and the cross-materia "Atrasados" view is mislabeled and lists one row per (alumno, dictado) instead of grouping by alumno. This change is a focused UX cleanup of those views — no new domain rules, governance BAJO with a single MEDIO backend touch.

## What Changes

- **Routing**: move the PROFESOR dictado LIST from `/profesor/dashboard` to `/dictados` and the detail from `/profesor/dictados/:dictadoId` to `/dictados/:dictadoId`, preserving the per-section children (`alumnos`, `actividades`, `atrasados`, `equipo`) and the AuthGuard/permission gating. Update the "Mis Dictados" nav item.
- **Breadcrumb**: render the dictado's human name (Materia — Cohorte) for the `:dictadoId` segment while the browser URL keeps the UUID. Today `Breadcrumbs.tsx` prints each path segment verbatim, so the UUID shows.
- **Header**: `DictadoDashboardPage` replaces "Panel del Dictado / ID: {uuid}" with `Materia — Cohorte`. A dictado is exactly ONE cohorte (DECISION LOCKED); cohorte is rendered flexibly (array-shaped) so multi-cohorte is a future no-op, but data stays single.
- **Backend (only touch, MEDIO)**: expose `materia_nombre` + `cohorte_nombre` on the dictado métricas response (join `Dictado→Materia`, `Dictado→Cohorte`), feeding the header, breadcrumb, and a shared name hook.
- **Padrón delete**: add a per-row delete button (single `DELETE .../padron/alumnos/{entrada_padron_id}`, already wired via `useMutationQuitarAlumno`). The reported "bulk baja doesn't work" bug is NOT visible from static reading — its fix is gated behind a runtime reproduction step; root cause is "to be confirmed by repro".
- **Registrar nota UX**: the modal becomes an inline new row inside the selected activity's table, pre-filled with that actividad. The alumno `<select>` shows ONLY alumnos not already graded in that activity. The vanilla "aprobado" checkboxes (create row + edit row) are restyled into the design system.
- **Refetch after mutations**: every profesor mutation also invalidates `['profesor','metricas',dictadoId]`, `['profesor','dashboard']`, `['profesor','atrasados',dictadoId]`, and `['profesor','atrasados-general']` so stat cards and the atrasados panel re-fetch.
- **Rename**: "Atrasados" → "Desaprobados/Atrasados" in the nav label and the cross-materia page heading; update `Sidebar.test.tsx`.
- **Comma-separated materias**: the cross-materia Desaprobados/Atrasados list groups rows by alumno (`entrada_padron_id`) and shows that alumno's materias comma-separated in one row (frontend-only grouping; per-materia activity breakdown collapses — accepted tradeoff). Backend endpoint unchanged.

Out of scope (owned by other changes): the "aprobado = booleano en todas las actividades" rule (`fix-regla-aprobado`); the per-row comunicado button and individual/general comunicado-without-actividad endpoints (`comunicado-profesor-individual-general`).

## Capabilities

### New Capabilities
- `profesor-dictado-ux`: routing, header naming, breadcrumb naming, padrón per-row delete, inline registrar-nota row with ungraded-alumno filtering, and cross-cutting cache invalidation for the PROFESOR dictado views.

### Modified Capabilities
- `atrasados-general-view`: the cross-materia delayed-students view is relabeled "Desaprobados/Atrasados" and groups rows by alumno with materias shown comma-separated. (The existing spec still describes the superseded per-materia `/atrasados` design; this delta also realigns it to the current `GET /api/v1/profesor/atrasados` single-endpoint implementation.)
- `metricas-frontend`: the dictado métricas response additionally carries `materia_nombre` and `cohorte_nombre` so the dictado views can display a human dictado name.

## Impact

- **Frontend**: `src/App.tsx` (routes), `src/features/layout/components/AppLayout.tsx` (nav items), `src/features/layout/components/Breadcrumbs.tsx`, `src/features/profesor/pages/DictadoDashboardPage.tsx`, `src/features/profesor/pages/AlumnosDictadoPage.tsx`, `src/features/profesor/pages/ActividadesDictadoPage.tsx`, `src/features/profesor/hooks/useProfesor.ts`, `src/features/profesor/types/index.ts`, `src/features/academico/pages/AtrasadosGeneralPage.tsx`, and `Sidebar.test.tsx`.
- **Backend (single touch)**: `app/services/profesor_service.py` (`get_metricas_dictado` + join to Materia/Cohorte) and its response schema/router; one Alembic migration is NOT expected (read-only join, no schema change).
- **No DB schema change, no new permissions.** Existing `atrasados:ver` / profesor permissions and routes' AuthGuards are preserved.
