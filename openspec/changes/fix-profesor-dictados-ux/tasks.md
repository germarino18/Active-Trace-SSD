# Tasks — fix-profesor-dictados-ux

> Strict TDD: write the failing test FIRST, then minimum code, then triangulate, then refactor.
> NO DB mocks — the one backend touch uses a real/ephemeral test DB.
> Conventional Commits, scope `ui` or `profesor`, NO Co-Authored-By.

## 1. Backend — métricas carries materia_nombre + cohorte_nombre (MEDIO)

- [ ] 1.1 RED: write a failing service test for `get_metricas_dictado` (`backend/app/services/profesor_service.py` ~line 180) asserting the response includes `materia_nombre` and `cohorte_nombre` resolved from the dictado's Materia and Cohorte — seeded in a real/ephemeral test DB, tenant-scoped. Add a second case (different materia/cohorte) for triangulation.
- [ ] 1.2 GREEN: join `Dictado→Materia` and `Dictado→Cohorte` (both columns exist on `models/dictado.py`) within the tenant scope and add `materia_nombre` + `cohorte_nombre` to the métricas dict, preserving existing metric fields.
- [ ] 1.3 Update the métricas Pydantic response schema to include the two new fields with `model_config = ConfigDict(extra='forbid')`; add/extend a router test asserting `GET /api/v1/profesor/dictados/{id}/metricas` returns them.
- [ ] 1.4 REFACTOR: keep the query in the repository layer (no DB access in the service); confirm tenant filter and soft-delete scoping; run the profesor service + router tests green.

## 2. Frontend — DictadoMetricas type + dictado-name hook

- [ ] 2.1 RED: add a test for the `DictadoMetricas` consumer expecting `materia_nombre` and `cohorte_nombre`; extend the type in `frontend/src/features/profesor/types/index.ts` (`DictadoMetricas`).
- [ ] 2.2 Add a hook (in `frontend/src/features/profesor/hooks/useProfesor.ts`) that derives the dictado display name `Materia — Cohorte` from `useDictadoMetricas(dictadoId)`, rendering the cohorte through an array-shaped structure (single element today) per design D3. Test: returns `"Materia — Cohorte"` and a neutral placeholder while loading (never the raw UUID).

## 3. Frontend — header shows Materia — Cohorte

- [ ] 3.1 RED: test `DictadoDashboardPage` (`frontend/src/features/profesor/pages/DictadoDashboardPage.tsx`) renders `Materia — Cohorte` and does NOT render "Panel del Dictado" nor "ID: {uuid}".
- [ ] 3.2 GREEN: replace the header block (lines ~18-25) to use the name hook from task 2.2; keep StatCards and tabs unchanged. Keep the component <200 LOC.

## 4. Frontend — breadcrumb shows dictado name for the UUID segment

- [ ] 4.1 RED: test `frontend/src/features/layout/components/Breadcrumbs.tsx` renders the dictado `Materia — Cohorte` name for a `:dictadoId` UUID segment while the URL keeps the UUID; a neutral placeholder while the name is unresolved.
- [ ] 4.2 GREEN: detect a dictado-UUID segment and resolve its label via the name hook (task 2.2); other segments unchanged. Avoid `any`.

## 5. Frontend — move routes to /dictados

- [ ] 5.1 Grep for callers of `/profesor/dashboard` and `/profesor/dictados/` across `frontend/src` (links, tests, redirects) and list them.
- [ ] 5.2 RED: test that the list renders at `/dictados` and the detail + children (`alumnos|actividades|atrasados|equipo`) render under `/dictados/:dictadoId`, with index redirecting to `alumnos`.
- [ ] 5.3 GREEN: in `frontend/src/App.tsx` (~lines 224-243) move the list element to `/dictados` and the detail subtree to `/dictados/:dictadoId`, keeping children and the AuthGuard/permission wrapper intact. Update any internal callers found in 5.1.
- [ ] 5.4 Update the "Mis Dictados" nav item in `frontend/src/features/layout/components/AppLayout.tsx` (~line 55) to `path: '/dictados'`; assert gating/permission unchanged. Update sidebar test if it asserts the path.

## 6. Frontend — padrón per-row delete + bulk-baja runtime repro

- [ ] 6.1 RUNTIME REPRO: run the app against a real/ephemeral DB, reproduce the reported "bulk baja doesn't work" on `AlumnosDictadoPage`, and record the observed behavior + root cause (or "not reproducible"). Do NOT change code before this.
- [ ] 6.2 If 6.1 confirms a bug: RED test capturing it, then GREEN the minimum fix in the bulk path (`useMutationQuitarAlumnosBulk` / `quitarAlumnosBulk` / 204 handling). If not reproducible, document that the per-row control (6.3) is the delivered remedy.
- [ ] 6.3 RED: test `AlumnosDictadoPage` (`frontend/src/features/profesor/pages/AlumnosDictadoPage.tsx`) renders a per-row delete control that, on confirm, calls `useMutationQuitarAlumno` (single `DELETE .../padron/alumnos/{entrada_padron_id}`) and refreshes the padrón; the alumno returns to disponibles.
- [ ] 6.4 GREEN: add the per-row delete button + confirm to each table row; keep the existing bulk baja. Component stays <200 LOC (extract a row component if needed).

## 7. Frontend — registrar nota inline in the activity (UX)

- [ ] 7.1 RED: test `ActividadesDictadoPage` (`frontend/src/features/profesor/pages/ActividadesDictadoPage.tsx`) renders the registrar-nota input as a new ROW inside the activity whose id equals `registrarNotaActividadId`, NOT at the top of the page, pre-filled with that actividad.
- [ ] 7.2 RED: test the alumno selector lists ONLY alumnos not already graded in that activity (filter `padron` against the activity's calificaciones via `matchGrade`/`buildVirtualActividades` on `entrada_padron_id`); empty/disabled when all are graded.
- [ ] 7.3 GREEN: move the `RegistrarNotaModal` content (~line 427/303-371) into an inline row in the matched activity table; compute the ungraded list; wire `useMutationRegistrarCalificacion`.
- [ ] 7.4 RED+GREEN: restyle the create-row and edit-row "aprobado" controls (lines ~371 and ~262) into the design system style; test the control renders the DS variant (not a bare native checkbox). Keep the page modular (<200 LOC per component; extract the inline-row component).

## 8. Frontend — refetch metrics + atrasados after mutations

- [ ] 8.1 RED: for each profesor mutation hook, test that `onSuccess` invalidates `['profesor','metricas',dictadoId]`, `['profesor','dashboard']`, `['profesor','atrasados',dictadoId]`, and `['profesor','atrasados-general']`.
- [ ] 8.2 GREEN: add a shared `invalidateDictadoDerived(queryClient, dictadoId)` helper in `frontend/src/features/profesor/hooks/useProfesor.ts` and call it from every mutation's `onSuccess`: agregar alumno (single+bulk), quitar alumno (single+bulk), crear/eliminar actividad, registrar/editar calificacion, CSV upload. For hooks lacking `dictadoId` (e.g. `useMutationEditarCalificacion`), thread the id through or invalidate the broad `['profesor','metricas']` prefix.
- [ ] 8.3 REFACTOR: audit all mutation hooks in the file to confirm none is missed; tests green.

## 9. Frontend — rename to "Desaprobados/Atrasados"

- [ ] 9.1 RED: test the nav item label in `AppLayout.tsx` (~line 69) reads "Desaprobados/Atrasados"; update `Sidebar.test.tsx` expectations to match.
- [ ] 9.2 GREEN: rename the nav label; update the page heading in `frontend/src/features/academico/pages/AtrasadosGeneralPage.tsx` (h2 "Alumnos Atrasados") to "Desaprobados/Atrasados".

## 10. Frontend — group atrasados by alumno, materias comma-separated

- [ ] 10.1 RED: test `AtrasadosGeneralPage` groups `AtrasadoGeneral[]` by `entrada_padron_id` into ONE row per alumno, showing that alumno's distinct `materia_nombre` values comma-separated; the subject filter still narrows the grouped rows; empty state preserved.
- [ ] 10.2 GREEN: implement frontend-only grouping over `data`; render the "Materias" cell comma-separated; keep the loading/empty states. Backend endpoint untouched. Note in code the accepted tradeoff that the per-materia `actividades_sin_entrega` breakdown collapses.

## 11. Verify

- [ ] 11.1 Run the affected frontend test suites and the backend profesor service/router tests; all green.
- [ ] 11.2 Manual smoke (real/ephemeral DB): `/dictados` list → open a dictado (header + breadcrumb show name) → padrón single delete → registrar nota inline → confirm stat cards + atrasados refresh → cross-materia "Desaprobados/Atrasados" grouped view.
