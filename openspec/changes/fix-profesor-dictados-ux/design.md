## Context

The PROFESOR dictado views were built by the `frontend-profesor` change. Current state, traced from code:

- **Routing** (`src/App.tsx` ~224-243): list at `/profesor/dashboard` (`ProfesorDashboardListPage`), detail at `/profesor/dictados/:dictadoId` (`DictadoDashboardPage`) with children `alumnos|actividades|atrasados|equipo`. Nav item "Mis Dictados" → `/profesor/dashboard` in `AppLayout.tsx:55`.
- **Breadcrumbs** (`Breadcrumbs.tsx`) split the pathname and render each segment verbatim, so a dictado UUID renders raw.
- **Header** (`DictadoDashboardPage.tsx`) shows "Panel del Dictado" + `ID: {dictadoId}`. It already calls `useDictadoMetricas(dictadoId)`, whose `DictadoMetricas` type (`types/index.ts`) carries metrics only — no `materia_nombre`/`cohorte_nombre`. Backend `get_metricas_dictado` (`profesor_service.py` ~180) returns `compute_metricas_materia(...)`; the `Dictado` model (`models/dictado.py`) has both `materia_id` and `cohorte_id` columns.
- **Padrón** (`AlumnosDictadoPage.tsx`) supports only bulk baja (checkbox-select → confirm → `useMutationQuitarAlumnosBulk` → `POST .../padron/alumnos/bulk-baja`). A single-baja hook `useMutationQuitarAlumno` (→ `DELETE .../padron/alumnos/{id}`) already exists but has no UI. The bulk path looks correctly wired (204 handled in axios client) so the reported bug is not statically visible.
- **Registrar nota** (`ActividadesDictadoPage.tsx`): `RegistrarNotaModal` renders at the top of the page (~line 427) above all activities; `registrarNotaActividadId` already identifies the target activity. Helpers `buildVirtualActividades`/`matchGrade` already correlate calificaciones to activities by `entrada_padron_id`. "aprobado" is a native checkbox in both the create modal (line ~371) and the edit row (line ~262).
- **Mutations** (`useProfesor.ts`): each mutation invalidates only its narrow key (padrón, actividades, calificaciones, …). None touch metrics/dashboard/atrasados, so stat cards and the atrasados panel go stale.
- **Cross-materia atrasados** (`AtrasadosGeneralPage.tsx`): reads `GET /api/v1/profesor/atrasados` → `AtrasadoGeneral[]` (each = one alumno in one dictado), renders one row per entry, heading "Alumnos Atrasados". Nav label "Atrasados" in `AppLayout.tsx:69`.

Constraints from the project hard rules: identity from JWT; tenant-scoped repos; Routers→Services→Repositories→Models; soft-delete only; Pydantic `extra='forbid'`; React components <200 LOC, no `any`, no class components; Strict TDD with NO DB mocks (real/ephemeral DB for the backend touch). Governance: BAJO for the frontend items, MEDIO for the single backend touch.

## Goals / Non-Goals

**Goals:**
- Canonical PROFESOR dictado routes under `/dictados` with gating preserved.
- Human dictado name (`Materia — Cohorte`) in header and breadcrumb, URL keeps the UUID.
- A per-row padrón delete control; a runtime-verified decision on the bulk-baja bug.
- Inline registrar-nota row scoped to its activity, listing only ungraded alumnos, with design-system "aprobado" controls.
- Cross-cutting cache invalidation so metrics/atrasados refresh after any mutation.
- Rename to "Desaprobados/Atrasados" and group the cross-materia list by alumno with comma-separated materias.
- One small, read-only backend addition: `materia_nombre` + `cohorte_nombre` on métricas.

**Non-Goals:**
- No change to the "aprobado es booleano en todas las actividades" rule (→ `fix-regla-aprobado`).
- No per-row comunicado button, no individual/general comunicado-without-actividad endpoints (→ `comunicado-profesor-individual-general`).
- No multi-cohorte data model. No DB schema change, no new permissions.

## Decisions

**D1 — Route move keeps the existing AuthGuard wrapper.** Move the list element to `{ path: '/dictados', element: <ProfesorDashboardListPage /> }` and the detail subtree to `{ path: '/dictados/:dictadoId', ... }` with the same children. Keep them inside whatever AuthGuard/permission wrapper they live under today so gating is unchanged. Update `AppLayout.tsx` "Mis Dictados" → `/dictados`. *Alternative considered:* add redirects from the old paths — deferred; the prior change is internal and not yet relied on by bookmarks, so a clean move is simpler. Note this in tasks as an optional follow-up if needed.

**D2 — Dictado name comes from the métricas endpoint (single backend touch).** The header already loads métricas; piggy-backing `materia_nombre` + `cohorte_nombre` on that response avoids a second request and a new endpoint. Backend joins `Dictado→Materia` and `Dictado→Cohorte` (both already on the model), tenant-scoped, read-only, returned via a Pydantic schema with `extra='forbid'`. *Alternative considered:* a tiny sibling endpoint `GET /dictados/{id}/nombre` — rejected as more surface for the same data. The breadcrumb consumes the name through a shared hook keyed by the `:dictadoId` param so both header and breadcrumb read one cache entry.

**D3 — Cohorte rendered array-shaped, data single.** DECISION LOCKED: a dictado = exactly one cohorte. The UI renders the cohorte through a structure that tolerates an array (e.g. `cohortes.join(', ')` over a single-element list) so a future multi-cohorte model is a rendering no-op. The backend returns a single `cohorte_nombre`; the frontend wraps it for display. No speculative multi-cohorte data is introduced.

**D4 — Padrón: add per-row delete AND gate the bulk bug behind repro.** The single-baja hook already exists; the only missing piece is a per-row control (icon button → confirm → `useMutationQuitarAlumno`). For the reported "bulk doesn't work", the first task is a RUNTIME reproduction (real app, real/ephemeral DB) because static reading shows the path wired correctly. The fix is conditional on what the repro reveals; the proposal treats root cause as "to be confirmed by repro".

**D5 — Registrar nota becomes an inline row in the activity table.** Move `RegistrarNotaModal`'s content into a row rendered inside the matched activity's table when `registrarNotaActividadId === act.id`, pre-filling the actividad. Compute the ungraded-alumno list by filtering `padron` against that activity's existing calificaciones via the existing `matchGrade`/`buildVirtualActividades` correlation on `entrada_padron_id`. Restyle the create-row and edit-row "aprobado" controls with the design system. *Alternative considered:* keep a modal but position it near the activity — rejected; an inline row matches the table-editing mental model and reuses the existing row styling.

**D6 — Centralize invalidations.** Add the four extra keys (`['profesor','metricas',dictadoId]`, `['profesor','dashboard']`, `['profesor','atrasados',dictadoId]`, `['profesor','atrasados-general']`) to every profesor mutation's `onSuccess`. To avoid drift, introduce a small shared helper (e.g. `invalidateDictadoDerived(queryClient, dictadoId)`) called from each `onSuccess`, then audit all mutation hooks: agregar/quitar alumno (single+bulk), crear/eliminar actividad, registrar/editar calificacion, CSV upload. Some hooks lack `dictadoId` in their factory signature (`useMutationEditarCalificacion`); thread the id through or invalidate the broad `['profesor','metricas']` prefix where the specific id is unavailable.

**D7 — Cross-materia grouping is frontend-only.** Group `AtrasadoGeneral[]` by `entrada_padron_id`; collect distinct `materia_nombre` per alumno and render comma-separated. The per-(alumno, dictado) `actividades_sin_entrega` breakdown collapses for the grouped row — accepted. Backend endpoint untouched. Rename heading and nav label to "Desaprobados/Atrasados" and update `Sidebar.test.tsx`.

## Risks / Trade-offs

- **Bulk-baja bug not reproducible / environment-specific** → the per-row delete (D4) is a guaranteed-working remedy regardless; the repro step prevents a blind code change that could mask the real cause.
- **Route move breaks deep links / saved tabs** → the children and gating are preserved; if any internal link still points at `/profesor/dashboard`, the route-move task includes a grep for callers. Optional redirect noted in D1.
- **Métricas join adds query cost** → it is one extra join on an already-loaded dictado row, tenant-scoped; negligible. Schema with `extra='forbid'` prevents accidental field leakage.
- **Grouping hides per-materia activity detail** (D7) → accepted by scope; the per-dictado atrasados tab still shows the full breakdown.
- **Invalidation over-fetch** → broadening invalidations triggers a few extra refetches; acceptable for correctness of stat numbers and the atrasados panel.

## Migration Plan

No data migration. Backend change is additive and read-only (no Alembic migration expected). Deploy order is irrelevant: the frontend tolerates the new fields being absent (falls back to placeholder per spec) and the backend addition is backward-compatible. Rollback = revert the change; no persisted state is affected.

## Open Questions

- Does any existing code or test link to `/profesor/dashboard` or `/profesor/dictados/:id` that must be updated alongside the route move? (Resolve via grep in the route-move task.)
- Exact root cause of the bulk-baja report — deferred to the runtime reproduction task (D4).
