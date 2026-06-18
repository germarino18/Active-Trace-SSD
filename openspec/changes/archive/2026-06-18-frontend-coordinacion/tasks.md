## 1. Feature Module Scaffolding and Shared Types

- [x] 1.1 Create `features/coordinacion/` directory structure: `{components,hooks,services,types,pages}`
- [x] 1.2 Define shared domain types in `features/coordinacion/types/index.ts`: `Docente`, `Asignacion`, `Equipo`, `Aviso`, `Tarea`, `ComentarioTarea`, `SlotEncuentro`, `InstanciaEncuentro`, `Convocatoria`, `ReservaColoquio`, `ProgramaMateria`, `FechaAcademica`, `MonitorData`
- [x] 1.3 Define API response types: `AsignacionesResponse`, `AvisosResponse`, `TareasResponse`, `EncuentrosResponse`, `ColoquiosResponse`, `ProgramasResponse`, `MonitorGeneralResponse`
- [x] 1.4 Create `features/coordinacion/components/DataTable.tsx` — reusable sortable/filterable table with column visibility toggle
- [x] 1.5 Create `features/coordinacion/components/FilterBar.tsx` — reusable filter bar with date range, multi-select, and free text search
- [x] 1.6 Create `features/coordinacion/components/ConfirmDialog.tsx` — reusable confirmation dialog with support for cascade delete warnings
- [x] 1.7 Create `features/coordinacion/components/HelpButton.tsx` — contextual help button

## 2. Equipos Docentes — Service, Hooks, and Pages

- [x] 2.1 Create `features/coordinacion/services/equipos.service.ts` with functions: `getMisEquipos()`, `getEquipos()`, `getDocentes()`, `crearAsignacion()`, `actualizarAsignacion()`, `eliminarAsignacion()`, `asignacionMasiva()`, `clonarEquipo()`, `modificarVigencia()`, `exportarEquipo()`
- [x] 2.2 Create `features/coordinacion/hooks/useEquipos.ts` — TanStack Query hooks for equipo data and mutations
- [x] 2.3 Create `features/coordinacion/pages/MisEquiposPage.tsx` — my-teams view (own assignments) for PROFESOR/TUTOR/NEXO with role, career, cohort, validity, status columns
- [x] 2.4 Create `features/coordinacion/pages/EquiposListPage.tsx` — full assignment list for COORDINADOR/ADMIN with filters (subject, career, cohort, user, role)
- [x] 2.5 Create `features/coordinacion/pages/AsignacionIndividualPage.tsx` — individual assignment CRUD form
- [x] 2.6 Create `features/coordinacion/pages/AsignacionMasivaPage.tsx` — bulk assignment form: multi-teacher select, subject×career×cohort×role selectors, validity input
- [x] 2.7 Create `features/coordinacion/pages/ClonarEquipoPage.tsx` — clone team form: source cohort, destination cohort, materia selector
- [x] 2.8 Create `features/coordinacion/pages/ModificarVigenciaPage.tsx` — bulk validity change form with date picker
- [x] 2.9 Create `features/coordinacion/pages/EquipoDetallePage.tsx` — detail view of a single equipo (materia×carrera×cohorte) with member list
- [x] 2.10 Implement CSV export trigger that downloads file via browser

## 3. Avisos — Service, Hooks, and Pages

- [x] 3.1 Create `features/coordinacion/services/avisos.service.ts` with functions: `getAvisos()`, `getAviso(id)`, `crearAviso()`, `actualizarAviso()`, `eliminarAviso()`, `confirmarAck(avisoId)`
- [x] 3.2 Create `features/coordinacion/hooks/useAvisos.ts` — TanStack Query hooks for aviso CRUD and acknowledgment
- [x] 3.3 Create `features/coordinacion/pages/AvisosListPage.tsx` — list of avisos with scope, severity, validity columns and ack counter (COORDINADOR/ADMIN) or personal pending list (all roles)
- [x] 3.4 Create `features/coordinacion/pages/AvisoCrearPage.tsx` — creation form: title, message, scope selector (Global/Materia/Cohorte/Rol), severity selector, validity date range, requires_ack toggle, ordering priority
- [x] 3.5 Create `features/coordinacion/pages/AvisoEditarPage.tsx` — edit form (pre-filled with existing data)
- [x] 3.6 Create `features/coordinacion/components/ScopeSelector.tsx` — scope type selector with conditional context picker (subject/cohort/role picker based on scope type)
- [x] 3.7 Implement acknowledgment button and counter display on aviso cards

## 4. Tareas Internas — Service, Hooks, and Pages

- [x] 4.1 Create `features/coordinacion/services/tareas.service.ts` with functions: `getMisTareas()`, `getTareas()`, `getTarea(id)`, `crearTarea()`, `cambiarEstado(tareaId, estado, razon)`, `agregarComentario(tareaId, contenido)`, `delegarTarea(tareaId, nuevoAsignado)`
- [x] 4.2 Create `features/coordinacion/hooks/useTareas.ts` — TanStack Query hooks for tarea CRUD, state changes, and comments
- [x] 4.3 Create `features/coordinacion/pages/MisTareasPage.tsx` — my-tasks view filterable by academic context for PROFESOR/TUTOR
- [x] 4.4 Create `features/coordinacion/pages/TareasListPage.tsx` — global admin view for COORDINADOR/ADMIN with filters (assigned user, assigner, subject, state, free search)
- [x] 4.5 Create `features/coordinacion/pages/TareaCrearPage.tsx` — create form: title, description, assigned user picker, academic context selector
- [x] 4.6 Create `features/coordinacion/pages/TareaDetallePage.tsx` — detail view with state transitions, delegation action, comment thread
- [x] 4.7 Create `features/coordinacion/components/CommentThread.tsx` — chronological comment list with add-comment form
- [x] 4.8 Create `features/coordinacion/components/TareaStateBadge.tsx` — colored badge for each state (Pendiente/En progreso/Resuelta/Cancelada)
- [x] 4.9 Implement state transition validation: only allow valid transitions per workflow

## 5. Encuentros — Service, Hooks, and Pages

- [x] 5.1 Create `features/coordinacion/services/encuentros.service.ts` with functions: `getEncuentros()`, `getEncuentro(id)`, `crearSlotRecurrente()`, `crearEncuentroUnico()`, `actualizarInstancia(id, data)`, `generarHtml(id)`
- [x] 5.2 Create `features/coordinacion/hooks/useEncuentros.ts` — TanStack Query hooks for encuentro CRUD and HTML generation
- [x] 5.3 Create `features/coordinacion/pages/EncuentrosListPage.tsx` — cross-tenant admin overview with filters (teacher, subject, state, date range)
- [x] 5.4 Create `features/coordinacion/pages/EncuentroCrearPage.tsx` — creation form with toggle recurring/one-off: subject, day, time, start date, weeks count (recurring), title, meet URL
- [x] 5.5 Create `features/coordinacion/pages/EncuentroDetallePage.tsx` — instance management: edit state, meet URL, recording URL, internal comment; HTML generation button with copy-to-clipboard
- [x] 5.6 Create `features/coordinacion/components/EncuentroInstanceRow.tsx` — single instance row with editable fields

## 6. Coloquios — Service, Hooks, and Pages

- [x] 6.1 Create `features/coordinacion/services/coloquios.service.ts` with functions: `getConvocatorias()`, `getConvocatoria(id)`, `crearConvocatoria()`, `importarAlumnos(convocatoriaId, file)`, `getMetricas(convocatoriaId)`, `reservarTurno(convocatoriaId, diaId)`, `getResultados(convocatoriaId)`
- [x] 6.2 Create `features/coordinacion/hooks/useColoquios.ts` — TanStack Query hooks for convocatoria CRUD, metrics, and reservations
- [x] 6.3 Create `features/coordinacion/pages/ConvocatoriasListPage.tsx` — tabular view with metrics columns: materia, instancia, días disponibles, convocados, reservas activas, cupos libres; management action buttons
- [x] 6.4 Create `features/coordinacion/pages/ConvocatoriaCrearPage.tsx` — creation form: subject selector, instance, days with date/slots/quotas per day
- [x] 6.5 Create `features/coordinacion/pages/ConvocatoriaDetallePage.tsx` — detail with tabs: students (import), reservations (list), metrics (KPIs), results (consolidated)
- [x] 6.6 Create `features/coordinacion/components/MetricasColoquio.tsx` — KPI cards: total alumnos, instancias activas, reservas, cupos libres

## 7. Programas y Fechas Académicas — Service, Hooks, and Pages

- [x] 7.1 Create `features/coordinacion/services/programas.service.ts` with functions: `getProgramas()`, `crearPrograma(file, data)`, `eliminarPrograma(id)`, `getFechasAcademicas()`, `crearFechaAcademica()`, `actualizarFechaAcademica(id)`, `generarHtmlFechas(subjectId, cohorteId)`
- [x] 7.2 Create `features/coordinacion/hooks/useProgramas.ts` — TanStack Query hooks for programas and fechas
- [x] 7.3 Create `features/coordinacion/pages/ProgramasListPage.tsx` — table of uploaded programs: materia, carrera, cohorte, título, fecha_subida; download link
- [x] 7.4 Create `features/coordinacion/pages/ProgramaCrearPage.tsx` — upload form: file selector (PDF), title, subject×career×cohort selectors
- [x] 7.5 Create `features/coordinacion/pages/FechasAcademicasPage.tsx` — tabular view of exam dates with toggle to calendar view; create/edit form; HTML generation button
- [x] 7.6 Create `features/coordinacion/components/CalendarioFechas.tsx` — monthly calendar component color-coded by type (partial/TP/colloquium)

## 8. Monitores Transversales — Service, Hooks, and Pages

- [x] 8.1 Create `features/coordinacion/services/monitores.service.ts` with functions: `getMonitorGeneral(filters)`, `getMonitorCoordinacion(filters)`
- [x] 8.2 Create `features/coordinacion/hooks/useMonitores.ts` — TanStack Query hooks with filter state for both monitor views
- [x] 8.3 Create `features/coordinacion/pages/MonitorGeneralPage.tsx` — general monitor (F2.7/19.1): actions-per-day chart, communication status by teacher, interactions by teacher×subject, last N actions log (configurable max)
- [x] 8.4 Create `features/coordinacion/pages/MonitorCoordinacionPage.tsx` — coordination monitor (F2.9): filterable by date range, subject, user; per-teacher/per-subject interaction data
- [x] 8.5 Create `features/coordinacion/components/ActionsChart.tsx` — simple bar/line chart for actions-per-day (using inline SVG or a lightweight approach)
- [x] 8.6 Implement role-based data scoping: COORDINADOR sees `(propio)` scope, ADMIN sees all

## 9. Routing and Sidebar Integration

- [x] 9.1 Add coordinacion routes to `App.tsx` under `AuthGuard / AppLayout`
- [x] 9.2 Update sidebar menu configuration with COORDINADOR and ADMIN groups requiring `equipos:*`, `avisos:*`, `tareas:*`, `encuentros:*`, `coloquios:*`, `programas:*`, `atrasados:*`, `auditoria:*` permissions

## 10. Tests

- [x] 10.1 Write test: `EquiposListPage` renders assignment table with filters and handles CRUD
- [x] 10.2 Write test: `AsignacionMasivaPage` form submits correctly with mocked API
- [x] 10.3 Write test: `ClonarEquipoPage` clone flow with success/empty state
- [x] 10.4 Write test: `AvisosListPage` renders avisos with correct scope and ack counter
- [x] 10.5 Write test: `AvisoCrearPage` creates aviso with scope selector
- [x] 10.6 Write test: `TareaDetallePage` state transitions and comment thread
- [x] 10.7 Write test: `TareasListPage` admin view filters correctly
- [x] 10.8 Write test: `EncuentrosListPage` renders instances with filters
- [x] 10.9 Write test: `ConvocatoriasListPage` renders convocation metrics table
- [x] 10.10 Write test: `MonitorGeneralPage` renders with charts and filter interaction
- [x] 10.11 Write test: Role-based rendering — PROFESOR sees only mis-equipos, COORDINADOR sees full list
- [x] 10.12 Write test: Empty states render correctly for each feature
