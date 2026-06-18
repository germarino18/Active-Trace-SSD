## Context

The COORDINADOR and ADMIN roles' frontend module is the third frontend change after C-21 (shell + auth) and C-22 (PROFESOR workspace). The backend exposes REST endpoints for teaching teams (C-08), transversal monitors (C-11), meetings (C-13), oral exams (C-14), announcements (C-15), internal tasks (C-16), and subject programs (C-17). Unlike C-22 (which operates within a single materia context), coordination features are **cross-subject and cross-tenant** — they manage the entire academic structure. The feature-based module structure, Tailwind CSS v4 theme tokens, Axios client with auth interceptors, and permission-based sidebar are already established by C-21 and followed by C-22.

## Goals / Non-Goals

**Goals:**
- Feature pages for COORDINADOR and ADMIN roles under `features/coordinacion/` following C-21/C-22 conventions
- **Equipos docentes**: my-teams view (own assignments by PROFESOR/TUTOR/NEXO with role, career, cohort, validity), assignment CRUD (COORDINADOR/ADMIN with filters: subject, career, cohort, user, role, report relation), bulk assignment (multi-teacher × subject × career × cohort × role), clone between periods, modify general validity, CSV export
- **Avisos**: full CRUD with scope (Global/Subject/Cohort/Role), severity (info/warning/critical), validity start/end dates, mandatory acknowledgment toggle, view filtered by user's role/scope/cohort, acknowledgment confirmation, counter display
- **Tareas internas**: my-tasks view (own assigned, filterable by academic context), assign/delegate task (traceable assigner/assignee), state workflow (Pendiente→En progreso→Resuelta→Cancelada), comment thread per task, global admin view (COORDINADOR/ADMIN with filters: assigned user, assigner, subject, state, free search)
- **Encuentros admin**: create recurring (weekly × N weeks) and one-off meeting slots, manage instances (state, meet_url, recording_url, internal comment), generate HTML block for LMS, cross-tenant admin overview
- **Coloquios/Evaluaciones**: create convocation (subject×instance×days×slots), import student roster, list all convocations with metrics (materia, instance, available-days, convocados, active-reservations, free-slots) and management actions, student self-reservation (by ALUMNO), consolidated results, admin global view
- **Programas y fechas**: upload and associate subject programs (document file by subject×career×cohort with descriptive title), manage exam dates (partial/TP/colloquium by subject×cohort×instance number with date and title), tabular + calendar view, LMS-ready content fragment generation
- **Monitores transversales**: general monitor (F2.7 — actions per day, communication status by teacher, interactions by teacher×subject, last N actions log) and coordination monitor (F2.9 — date range, subject, user filters)
- **New sidebar menu items** for COORDINADOR and ADMIN requiring `equipos:*`, `avisos:*`, `tareas:*`, `encuentros:*`, `coloquios:*`, `programas:*`, `atrasados:*` permissions
- **Routes** under `AuthGuard / AppLayout` as top-level pages (not nested under `/materias/:id`)
- **Shared components** extracted to `features/coordinacion/components/` for filters, advanced tables, and form patterns
- **Tests covering**: equipos CRUD and clone, avisos publication and scope filtering, tareas workflow state machine, monitores filtering

**Non-Goals:**
- FINANZAS features (C-24 — liquidaciones, facturas, grilla salarial)
- ADMIN structure CRUD (carreras, cohortes, materias — deferred to C-24)
- ADMIN user management (deferred to C-24)
- Auditoría panel (C-19 — deferred to C-24)
- E2E tests (frontend tests use mocked API)
- Backend changes
- Real-time WebSocket connections (status tracking uses TanStack Query `refetchInterval`)
- File drag-and-drop (uses standard `<input type="file">`)

## Decisions

### 1. Feature module structure: `features/coordinacion/`
- **Decision**: A single `features/coordinacion/` module with sub-folders `{components,hooks,services,types,pages}`. Each sub-feature (equipos, avisos, tareas, encuentros, coloquios, programas, monitores) gets its own files within those folders.
- **Rationale**: Follows the C-22 convention (`features/academico/`). The domain is cohesive (all COORDINADOR/ADMIN features share entity types like `Docente`, `Materia`, `Asignacion`, `Usuario`). 
- **Alternatives considered**: Separate feature modules per sub-feature (would duplicate shared types like `Docente`, `MateriaContext`, `AsignacionFilter` — too much overhead for the shared domain).

### 2. Component tree and routing
- **Decision**: Top-level routes without a shared context param. Each feature section has its own layout wrapper with section-specific navigation tabs. Routes:

  ```
  /equipos                     → EquiposDashboard (mis-equipos for PROFESOR/TUTOR/NEXO, full list for COORDINADOR/ADMIN)
  /equipos/asignar             → AsignacionIndividualPage (COORDINADOR/ADMIN)
  /equipos/masiva              → AsignacionMasivaPage
  /equipos/clonar              → ClonarEquipoPage
  /equipos/vigencia            → ModificarVigenciaPage
  /equipos/export              → ExportarEquipoPage (CSV download)
  /equipos/:id                 → EquipoDetallePage

  /avisos                      → AvisosListPage
  /avisos/nuevo                → AvisoCrearPage
  /avisos/:id/editar           → AvisoEditarPage

  /tareas                      → TareasListPage (global admin view for COORDINADOR/ADMIN, my-tasks for PROFESOR/TUTOR)
  /tareas/nueva                → TareaCrearPage
  /tareas/:id                  → TareaDetallePage (with comment thread)

  /encuentros                  → EncuentrosListPage (admin overview)
  /encuentros/nuevo            → EncuentroCrearPage (recurring or one-off)
  /encuentros/:id              → EncuentroDetallePage (instance management)

  /coloquios                   → ConvocatoriasListPage (with metrics)
  /coloquios/nuevo             → ConvocatoriaCrearPage
  /coloquios/:id               → ConvocatoriaDetallePage (students, reservations, results)

  /programas                   → ProgramasListPage
  /programas/nuevo             → ProgramaCrearPage (upload + associate)
  /fechas                      → FechasAcademicasPage (tabular + calendar)

  /monitores/general           → MonitorGeneralPage
  /monitores/coordinacion      → MonitorCoordinacionPage
  ```
- **Rationale**: Unlike C-22 (where all actions are within a single materia context), coordination features span multiple subjects, cohorts, and users simultaneously. A shared context param would be misleading.
- **Alternatives considered**: Sidebar mega-menu with all features flat (better UX for quick access) vs grouped dropdowns (cleaner but adds click friction). Decision: flat menu by feature domain with sub-items.

### 3. API service layer
- **Decision**: Each sub-feature gets a dedicated service file (`services/equipos.service.ts`, `services/avisos.service.ts`, etc.) calling the typed API helpers (`get`, `post`, `patch`, `del` from `shared/services/api.ts`).
- **Rationale**: Same pattern as C-22. Keeps API calls organized by domain.
- **Key endpoints consumed**:
  - **Equipos**: `GET /api/v1/equipos/mis-equipos`, `GET /api/v1/equipos`, `GET /api/v1/equipos/docentes`, `POST /api/v1/equipos/asignacion-masiva`, `POST /api/v1/equipos/clonar`, `PATCH /api/v1/equipos/vigencia`, `GET /api/v1/equipos/export`, `POST /api/v1/asignaciones`, `PATCH /api/v1/asignaciones/:id`, `DELETE /api/v1/asignaciones/:id`
  - **Avisos**: `GET /api/v1/avisos`, `POST /api/v1/avisos`, `GET /api/v1/avisos/:id`, `PATCH /api/v1/avisos/:id`, `DELETE /api/v1/avisos/:id`, `POST /api/v1/avisos/:id/ack`
  - **Tareas**: `GET /api/v1/tareas`, `GET /api/v1/tareas/mias`, `POST /api/v1/tareas`, `GET /api/v1/tareas/:id`, `PATCH /api/v1/tareas/:id/estado`, `POST /api/v1/tareas/:id/comentarios`
  - **Encuentros**: `POST /api/v1/encuentros/slot`, `GET /api/v1/encuentros`, `GET /api/v1/encuentros/:id`, `PATCH /api/v1/encuentros/:id`, `GET /api/v1/encuentros/:id/html`
  - **Coloquios**: `POST /api/v1/coloquios`, `GET /api/v1/coloquios`, `GET /api/v1/coloquios/:id`, `POST /api/v1/coloquios/:id/importar`, `POST /api/v1/coloquios/:id/reservar`, `GET /api/v1/coloquios/:id/metricas`
  - **Programas**: `POST /api/v1/programas`, `GET /api/v1/programas`, `GET /api/v1/programas/:id`, `DELETE /api/v1/programas/:id`, `GET /api/v1/fechas-academicas`, `POST /api/v1/fechas-academicas`, `PATCH /api/v1/fechas-academicas/:id`
  - **Monitores**: `GET /api/v1/monitor/general`, `GET /api/v1/monitor/coordinacion`

### 4. Form patterns: React Hook Form + Zod
- **Decision**: All complex forms (asignación masiva, aviso CRUD, tarea create, encuentro create, convocatoria create, programa upload) use React Hook Form with Zod validation schemas, following the pattern from C-21/C-22.
- **Rationale**: Established pattern. Zod schemas can mirror backend Pydantic validation for consistent error messages.
- **Key schemas needed**: `asignacionMasivaSchema`, `avisoSchema`, `tareaSchema`, `encuentroSlotSchema`, `convocatoriaSchema`, `programaSchema`, `fechaAcademicaSchema`

### 5. Shared components for coordination
- **Decision**: Extract reusable components to `features/coordinacion/components/`:
  - `DataTable` — advanced sortable/filterable table with column visibility toggle (extends the simpler table from shared)
  - `FilterBar` — composed filters (date range, multi-select for subjects/cohorts/states, free text search)
  - `ConfirmDialog` with cascade delete warning for destructive actions
  - `HelpButton` with contextual help text (following dashboard-crud-page skill)
- **Rationale**: Coordination features share heavy filtering and data display patterns. A shared `DataTable` + `FilterBar` avoids repetition across 7 sub-features.
- **Alternatives considered**: Using only the generic table from `shared/` (too basic for multi-column sort + filter coordination UIs).

### 6. Bulk operations feedback
- **Decision**: Bulk operations (asignación masiva, clonar equipo) show a progress modal with per-item status using TanStack Query mutations + optimistic updates where safe.
- **Rationale**: These operations process multiple server-side records and may take time. The modal shows real-time progress and disables navigation until completion.
- **Pattern**: `useMutation` with `onMutate` (show modal) and `onSettled` (hide modal + invalidate queries).

### 7. Role-aware rendering
- **Decision**: Every coordination page checks the user's permissions from the JWT + `useAuth()` context and adapts the UI:
  - PROFESOR/TUTOR see only their own data (mis-equipos, mis-tareas, monitor filtered to their subjects)
  - COORDINADOR sees filtered by their scope (propio) plus cross-subject where permitted
  - ADMIN sees all
- **Rationale**: The backend enforces RBAC, but the frontend should hide actions the user cannot take to avoid confusion (e.g., hide "Asignación masiva" button for PROFESOR).
- **Pattern**: Reuse `usePermissions()` hook from `features/auth/`.

### 8. Styling
- **Decision**: All new components use Tailwind utility classes exclusively, following the theme tokens from C-21 (`bg-surface`, `border-outline-variant`, `text-on-surface`, `text-primary`).
- **Pattern**: Follow C-22 conventions — data tables, cards, forms, modals all use the same token-based design.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| **7 sub-features in one module creates large files** | Enforce the existing <200 LOC per component rule. Extract reusable logic to hooks. If `features/coordinacion/` grows beyond 15 files, split into `features/coordinacion-equipos/`, `features/coordinacion-avisos/`, etc. in a future refactor. |
| **Bulk operations (clonar, masiva) may timeout** | Configure Axios `timeout: 120s` for bulk endpoints. Show upload/processing progress indicator. Backend already wraps these in single transactions with audit. |
| **Cross-feature type dependencies** (e.g., `Docente` used by equipos, tareas, coloquios) | Define shared types in `features/coordinacion/types/index.ts`. Any type used by 3+ sub-features gets a dedicated file. |
| **Permission complexity** — multiple roles see different views of the same route | Each page component has a `roleSwitch` or early return: `if (isAlumno()) return null`. This is explicit, not hidden in a generic component. |
| **C-23 size risk** — 7 features may exceed manageable session size | Each sub-feature is independent. Implementation order: equipos → avisos → tareas → encuentros → coloquios → programas → monitores. If time runs out, deferred features are clearly scoped. |
