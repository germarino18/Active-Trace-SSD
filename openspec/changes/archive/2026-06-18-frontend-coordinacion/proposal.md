## Why

The backend domain features for COORDINADOR and ADMIN roles are complete (equipos via C-08, encuentros via C-13, coloquios via C-14, avisos via C-15, tareas via C-16, programas via C-17, monitores via C-11, auditoría via C-19). C-21 established the frontend shell (auth, layout, routing, HTTP client) and C-22 delivered the PROFESOR workspace. C-23 delivers the COORDINADOR/ADMIN workspace: manage teaching teams, publish announcements, oversee internal tasks, administer meetings and oral exams, configure academic calendars, and monitor transversal metrics. Without this, the platform is unusable for its coordination and administration roles.

## What Changes

- **New `features/coordinacion/` module** with 7 sub-features following the feature-based pattern from C-22
- **Equipos docentes pages**: mis-equipos view (own assignments), team management (CRUD assignments), bulk assignment, clone between periods, modify validity dates, CSV export (consumes `C-08` endpoints)
- **Avisos pages**: full CRUD with scope selector (Global/Materia/Cohorte/Rol), severity, validity period, acknowledgment tracking with counters (consumes `C-15` endpoints)
- **Tareas internas pages**: my-tasks view with workflow transitions, assign/delegate task with commentary thread, global admin view with filters by user/subject/state (consumes `C-16` endpoints)
- **Encuentros admin pages**: create recurring/one-off meeting slots, manage instances (state, meet URL, recording URL), generate HTML block for LMS, cross-tenant meeting overview (consumes `C-13` endpoints)
- **Coloquios pages**: create exam convocations with slots and quotas, import students to convocation, student self-reservation, metrics panel (convocados/reservas/libres), consolidated results (consumes `C-14` endpoints)
- **Programas y fechas pages**: upload and associate subject programs, manage exam dates (tabular + calendar view) (consumes `C-17` endpoints)
- **Monitores transversales**: general monitor (F2.7) and coordination monitor (F2.9) with date range filters (consumes `C-11` endpoints)
- **New routes** in `App.tsx` under the existing `AuthGuard / AppLayout` shell
- **Sidebar menu items** for COORDINADOR and ADMIN added to the permission-based navigation
- **Test suite**: ABM equipos, clonado, publicación de aviso, workflow de tarea, filtros de monitor

### What is OUT of scope (deferred to C-24)
- FINANZAS features (liquidaciones, facturas, grilla salarial)
- ADMIN structure features (carreras, cohortes, materias CRUD — these consume C-06)
- ADMIN user management (consumes C-07)
- Auditoría panel (consumes C-19)
- E2E tests (frontend tests use mocked API)
- Any backend changes

## Capabilities

### New Capabilities

- `equipos-frontend`: Teaching team management — my-teams view for PROFESOR/TUTOR/NEXO, full assignment CRUD for COORDINADOR/ADMIN, bulk assignment by subject×career×cohort×role, clone between periods, validity modification, CSV export
- `avisos-frontend`: Announcement CRUD — create/edit/delete with scope selector (Global/Subject/Cohort/Role), severity (info/warning/critical), validity window, mandatory acknowledgment, acknowledgment counters per user
- `tareas-frontend`: Internal task workflow — my-tasks filtered by academic context, assign/delegate task with assigner/assignee traceability, state workflow (Pendiente→En progreso→Resuelta→Cancelada), comment thread, global admin view with filters
- `encuentros-frontend`: Meeting administration — recurring slot creation (weekly × N weeks), one-off meetings, instance editing (state, meet URL, recording URL, internal comment), HTML block generation for LMS, cross-tenant admin overview
- `coloquios-frontend`: Oral exam management — create convocation with subject×instance×days×slots, import student roster, list convocations with metrics (convocados/reservas/cupos-libres), student self-reservation, consolidated results
- `programas-fechas-frontend`: Subject programs and academic dates — upload and associate program documents by subject×career×cohort, manage exam dates (partial/TP/colloquium) by subject×cohort×instance number, tabular and calendar views
- `monitores-frontend`: Transversal monitoring — general monitor with system-wide metrics, coordination monitor with per-teacher/per-subject interaction data, date range filters

### Modified Capabilities

*(None — first coordination frontend module, no existing coordination frontend specs to modify)*

## Impact

- New `frontend/src/features/coordinacion/` directory with `{components,hooks,services,types,pages}` sub-folders
- New routes added to `App.tsx` within the `AuthGuard / AppLayout` hierarchy:
  - `/equipos`, `/equipos/:id`, `/equipos/masiva`, `/equipos/clonar`
  - `/avisos`, `/avisos/nuevo`, `/avisos/:id/editar`
  - `/tareas`, `/tareas/mias`, `/tareas/:id`, `/tareas/nueva`
  - `/encuentros`, `/encuentros/nuevo`, `/encuentros/:id`
  - `/coloquios`, `/coloquios/nuevo`, `/coloquios/:id`
  - `/programas`, `/fechas`
  - `/monitores/general`, `/monitores/coordinacion`
- Sidebar menu configuration updated with COORDINADOR and ADMIN menu items (requiring `equipos:*`, `avisos:*`, `tareas:*`, `encuentros:*`, `coloquios:*`, `programas:*`, `atrasados:*` permissions)
- Tests: Vitest + React Testing Library with mocked Axios for equipos CRUD, avisos publication, tareas workflow, monitores filtering
- No backend changes required — consumes existing `C-08`, `C-11`, `C-13`, `C-14`, `C-15`, `C-16`, `C-17` endpoints
