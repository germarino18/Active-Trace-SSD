## Why

El frontend actual mezcla páginas completamente implementadas con stubs vacíos, y las páginas implementadas usan Tailwind directamente sin pasar por el sistema de componentes del design system Obsidian (`activia-trace-design`). El resultado es inconsistencia visual, componentes duplicados sin contrato, y ~40 páginas que muestran placeholders al usuario. Este change unifica el lenguaje visual y completa la implementación de todas las vistas, adoptando la skill `activia-trace-design` como sistema de componentes canónico.

## What Changes

- **Adopción del DS bundle**: `_ds_bundle.js` y `styles.css` de `activia-trace-design` se incorporan como base compartida de componentes (`Button`, `Card`, `StatCard`, `Badge`, `Tabs`, `NavItem`, `EmptyState`, etc.)
- **Rediseño de páginas implementadas**: `LoginPage`, `TwoFactorPage`, `MisMateriasPage` y otras ya funcionales se reescriben sobre los componentes del DS, manteniendo su lógica intacta
- **Implementación de stubs**: las ~40 páginas placeholder se conectan al backend existente y reciben UI completa siguiendo los UI kits del DS (login/2FA, dashboard, Mis Materias 5-tab, Mi Perfil, 403/404)
- **Páginas por dominio** (Opción B — redesign + integración real):
  - `auth`: Login, TwoFactor, ForgotPassword, ResetPassword
  - `shell`: DashboardPage, ProfilePage, NotFoundPage, ForbiddenPage
  - `alumno`: AlumnoDashboard, MisMaterias, MateriaDetalle, MisAvisos, MisColoquios, MisComunicaciones, MisFechas, MisProgramas, AlumnoInbox, AlumnoHilo, ComunicacionDetalle
  - `academico`: MateriaList + 5 tabs (ImportarCalificaciones, VistaAtrasados, ComunicacionAtrasados, EntregasSinCorregir, MonitorSeguimiento)
  - `tutor`: TutorAlumnos, GuardiasList, TutorEntregasSinCorregir
  - `admin`: Usuarios, Carreras, Cohortes, Materias, EstructuraAcademica, Auditoria, Metricas
  - `coordinacion`: Equipos, Encuentros, Convocatorias, Tareas, Programas, Avisos, Asignacion + helpers
  - `finanzas`: Liquidaciones, GrillaSalarial, Facturas

## Capabilities

### New Capabilities

- `ui-auth`: Pantallas de autenticación (login, 2FA, recupero de contraseña) con el UI kit Obsidian
- `ui-shell`: Dashboard principal, perfil de usuario, páginas de error 403/404
- `ui-alumno`: Suite completa de vistas del rol Alumno
- `ui-academico`: Vista de materias del profesor con las 5 tabs del flujo académico central
- `ui-tutor`: Vistas del rol Tutor (alumnos asignados, guardias, entregas)
- `ui-admin`: Panel de administración (usuarios, estructura académica, auditoría, métricas)
- `ui-coordinacion`: Suite de coordinación (equipos, encuentros, convocatorias, tareas, programas, avisos)
- `ui-finanzas`: Vistas de liquidaciones y facturación

### Modified Capabilities

<!-- Sin cambios de requisitos en specs existentes — este change es puramente de capa de presentación -->

## Impact

- **Frontend** (`frontend/src/features/*/`, `frontend/src/pages/`): todos los archivos de páginas y componentes de UI
- **Sin cambios de API**: los endpoints backend no se modifican; sí se completa la integración en páginas que hoy son stub
- **Dependencia nueva**: `activia-trace-design` skill como fuente canónica de componentes y tokens (ya instalada en `.agents/skills/`)
- **Tests frontend**: los tests existentes en `frontend/src/test/` deberán actualizarse para reflejar el nuevo marcado HTML
- **Sin cambios de routing**: las rutas en `App.tsx` no se modifican
