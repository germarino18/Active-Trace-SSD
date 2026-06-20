# Tasks — frontend-profesor

> Gobernanza: las tareas marcadas **[CRÍTICO — bloqueada-en-aprobación]** tocan RBAC o comunicaciones y NO se implementan sin aprobación humana explícita. El resto puede avanzar de forma autónoma con tests en verde (Strict TDD: test que falla → código mínimo → triangulación → refactor).

## 1. Modelo de datos y migración (autónomo)

- [x] 1.1 Crear modelo `Actividad` en `backend/app/models/actividad.py` (`dictado_id`, `nombre`, `tipo`, `fecha_limite`) con `BaseMixin`/`TenantMixin` y soft delete; registrar en `app/models/__init__.py`
- [x] 1.2 Agregar columna `actividad_id : FK → actividad.id` nullable a `Calificacion` en `backend/app/models/calificacion.py` + índice por `tenant_id, actividad_id`
- [x] 1.3 Generar UNA migración Alembic aditiva (crea tabla `actividad` + columna FK nullable + índice); verificar upgrade y downgrade
- [x] 1.4 Repository de `Actividad` (`backend/app/repositories/`) con filtrado por `tenant_id` por defecto y exclusión de soft-deleted

## 2. RBAC — nuevos permisos [CRÍTICO — bloqueada-en-aprobación]

- [x] 2.1 Definir `Perm.ACTIVIDADES_GESTIONAR = "actividades:gestionar"`, `Perm.CALIFICACIONES_EDITAR = "calificaciones:editar"`, `Perm.PADRON_GESTIONAR_ALUMNO = "padron:gestionar-alumno"` en `backend/app/core/permissions.py`
- [x] 2.2 Seed de roles: otorgar los nuevos permisos a PROFESOR (y COORDINADOR/ADMIN según corresponda)
- [x] 2.3 Tests de autorización fail-closed para cada nuevo permiso (sin permiso → 403)

## 3. CRUD Actividad — backend (autónomo)

- [x] 3.1 Schemas Pydantic de Actividad (create/update/response) con `extra='forbid'`
- [x] 3.2 Servicio de Actividad (crear sin notas, listar por dictado, editar `fecha_limite`, soft-delete) vía repository
- [x] 3.3 Endpoints CRUD Actividad por dictado con `require_permission(Perm.ACTIVIDADES_GESTIONAR)` (router `actividades` o extensión de `calificaciones`)
- [x] 3.4 Garantizar que la carga de calificación contra una Actividad pueble `actividad` (=`Actividad.nombre`) y `actividad_id` consistentes; test de la invariante
- [x] 3.5 Tests: crear sin notas, listar sólo vivas, editar fecha, soft-delete, aislamiento de tenant

## 4. Dashboard profesor y métricas por dictado — backend (autónomo)

- [x] 4.1 Servicio dashboard-profesor: derivar dictados del usuario por `Asignacion` rol=PROFESOR vigente (reusar `find_roles_vigentes`); agregar materias asignadas, alumnos, encuentros, atrasados totales, scopeado a tenant de la sesión
- [x] 4.2 Endpoint dashboard-profesor (identidad desde JWT, sin parámetros de identidad en la petición)
- [x] 4.3 Endpoint métricas por dictado envolviendo `compute_metricas_materia` (campos: total_alumnos, aprobados, atrasados, total_actividades, promedio_general, sin_datos)
- [x] 4.4 Tests: profesor con/sin dictados, asignación vencida excluida, dictado de otro tenant → 404, `sin_datos` cuando no hay calificaciones

## 5. Edición de calificación — backend [CRÍTICO — bloqueada-en-aprobación]

- [x] 5.1 Schema de edición (nota numérica/textual + aprobado) con `extra='forbid'`
- [x] 5.2 Servicio de edición individual de calificación con registro en auditoría (autor desde sesión)
- [x] 5.3 Endpoint PATCH calificación con `require_permission(Perm.CALIFICACIONES_EDITAR)`, scopeado a tenant
- [x] 5.4 Tests: editar nota+aprobado, sin permiso → 403, otro tenant → 404, campo no declarado → rechazo, evento de auditoría registrado

## 6. Gestión de alumnos del dictado — backend [CRÍTICO — bloqueada-en-aprobación para alta/baja; export autónomo]

- [x] 6.1 [CRÍTICO] Servicio + endpoint alta individual de alumno al padrón del dictado con `require_permission(Perm.PADRON_GESTIONAR_ALUMNO)` y auditoría
- [x] 6.2 [CRÍTICO] Servicio + endpoint baja individual (soft delete) de alumno del padrón con `require_permission(Perm.PADRON_GESTIONAR_ALUMNO)` y auditoría
- [x] 6.3 [autónomo] Endpoint export plantilla CSV precargada con padrón vigente (`alumno_id`, `nombre`, `apellido` + columnas vacías), sólo lectura, sin auditoría
- [x] 6.4 Tests: alta/baja con y sin permiso, soft-delete (no hard), export con alumnos, aislamiento de tenant

## 7. Atrasados del profesor y clasificación — backend (autónomo salvo comunicado)

- [x] 7.1 Servicio de clasificación Aprobado/Atrasado reusando `compute_alumno_atrasado`; refinar faltantes en atrasado-null sólo si `Actividad.fecha_limite < hoy`
- [x] 7.2 Endpoint que devuelve alumnos clasificados (desaprobado vs atrasado-null con actividad faltante), scopeado a tenant
- [x] 7.3 Tests: aprobado, desaprobado, atrasado-null (fecha vencida), faltante sin fecha límite NO es atrasado-null

## 8. Comunicado a atrasado-null — backend [CRÍTICO — bloqueada-en-aprobación]

- [x] 8.1 Servicio que prepara el comunicado para atrasado-null (referencia actividad + materia) sobre el pipeline existente (preview → enviar_masivo → aprobación)
- [x] 8.2 Endpoint de disparo del comunicado con identidad/tenant desde sesión y circuito de aprobación de comunicaciones
- [x] 8.3 Tests: comunicado referencia actividad+materia, aislamiento de tenant (otro tenant → 404)

## 9. Equipo docente por dictado compartido — backend (autónomo)

- [x] 9.1 Extender `equipo_service`/repository para listar PROFESOR/TUTOR con `Asignacion` vigente al MISMO `dictado_id` (misma materia+cohorte), excluyendo vencidas y soft-deleted
- [x] 9.2 Endpoint de equipo del dictado para el profesor (exige asignación vigente al dictado), scopeado a tenant
- [x] 9.3 Filtros "míos": avisos por `created_by`, coloquios/evaluaciones emitidos por mí (reusar patrón de `tareas/mias`)
- [x] 9.4 Tests: compañeros del mismo dictado, exclusión de otra cohorte de la misma materia, exclusión de vencidas, aislamiento de tenant

## 10. Frontend — feature profesor (autónomo)

- [x] 10.1 Crear estructura `frontend/src/features/profesor/{components,hooks,services,types,pages}`
- [x] 10.2 Service + hooks TanStack Query para dashboard-profesor y métricas por dictado
- [x] 10.3 Actualizar `frontend/src/pages/DashboardPage.tsx` para consumir el dashboard-profesor real (eliminar stats hardcodeadas "—")
- [x] 10.4 Panel del dictado con las 6 métricas + layout de tabs (reusar `MateriaLayout`)
- [x] 10.5 Tab Alumnos: agregar/quitar alumno, ver info, descargar plantilla CSV (form RHF+Zod, sin `any`)
- [x] 10.6 Tab Calificaciones/Actividades: listar actividades + notas por alumno + estado aprobado; editar nota y aprobado; reusar `ImportarCalificacionesPage`
- [x] 10.7 Tab Atrasados: separar Aprobado/Atrasado y subtipos desaprobado vs atrasado-null; acción de comunicado (reusar `VistaAtrasadosPage`/`ComunicacionAtrasadosPage`)
- [x] 10.8 Tab Equipo docente: compañeros del mismo dictado
- [x] 10.9 Tab Avisos míos, Tab Mis tareas (editar estado/crear), Tab Mis coloquios (cambiar estados)
- [x] 10.10 Rutas y entrada de sidebar para PROFESOR; componentes <200 LOC, sin class components

## 11. Cierre (autónomo)

- [x] 11.1 Frontend tests: 414/414 passing (Vitest). Backend tests: 50/50 (test_profesor + test_actividades) + 898 broader suite. All green.
- [x] 11.2 Confirmed: `frontend/src/features/alumno/`, `frontend/src/features/admin/`, `backend/app/services/alumno_service.py`, `backend/app/schemas/alumno.py` have ZERO git diff modifications. Alumno feature is unmodified.
- [x] 11.3 Marked `[x]` in CHANGES.md under new entry `frontend-profesor` (no pre-existing C-NN was assigned — noted in CHANGES.md). `/opsx:archive` left for orchestrator.

## 12. Runtime bug fixes (fixed-professor-views branch)

Root cause: unit tests mocked the API, so runtime 403s/shape mismatches were invisible.

- [x] 12.1 **NEW** `GET /api/v1/profesor/dictados/{id}/padron` gated with `Perm.PADRON_GESTIONAR_ALUMNO` (PROFESOR has this); `service.obtener_padron_activo()` added. Integration tests: returns entries, 404 on missing dictado, 403 fail-closed, tenant isolation.
- [x] 12.2 **NEW** `GET /api/v1/profesor/dictados/{id}/alumnos-disponibles` — lists tenant alumnos NOT in current padron. Gated with `Perm.PADRON_GESTIONAR_ALUMNO`. Service method `get_alumnos_disponibles()` added. Integration tests: returns alumnos, excludes already-in-padron, 403 fail-closed.
- [x] 12.3 **CHANGED** `POST /api/v1/profesor/dictados/{id}/padron/alumnos` — accepts `usuario_id` (primary path) to link existing alumno, with name/email resolved from profile. Fallback: free-text (nombre+apellidos). Idempotent-safe: 409 if usuario_id already in padron. 422 if neither provided. Integration tests: 201, 409 idempotent, 422 missing body, 404 unknown usuario_id.
- [x] 12.4 **FIXED** `GET /api/admin/calificaciones/dictados/{id}` — response now includes `actividad_id` (was missing from `listar_calificaciones`). `response_model` removed to allow the extra field through. Integration tests: actividad_id is None for legacy rows, correct UUID for entity-linked rows.
- [x] 12.5 **FIXED** `frontend/.../profesor.service.ts` `getPadronDictado`: was `/api/admin/padron/dictados/${id}` (403); now `/api/v1/profesor/dictados/${id}/padron`.
- [x] 12.6 **FIXED** `frontend/.../profesor.service.ts` `getCalificacionesDictado`: was `/api/v1/calificaciones/...` (404 — wrong prefix); now `/api/admin/calificaciones/dictados/${id}`.
- [x] 12.7 **FIXED** `AvisosMiosPage.tsx`: was reading `data.items.length`/`data.items.map` (runtime crash); backend returns plain array. Fixed to use `avisos` directly. `AvisosProfesorResponse` type changed from `{items, total}` to `AvisoProfesor[]`.
- [x] 12.8 **FIXED** `CalificacionesDictadoPage.tsx`: was filtering by `actividad_id` only (0 results for legacy rows). Now shows union of Actividad entities + distinct `calificacion.actividad` strings. Match logic: `actividad_id` match preferred, fallback to name match. Alumno shown via padron lookup by `entrada_padron_id`.
- [x] 12.9 **FIXED** `AlumnosDictadoPage.tsx`: replaced free-text create form with `alumnos-disponibles` picker. Submits `{ usuario_id }` to the alta endpoint. After add/remove both `padron` and `alumnos-disponibles` queries are invalidated.
- [x] 12.10 **FIXED** `AlumnosDictadoPage.test.tsx`: added `useAlumnosDisponibles` to vi.mock + `mockAlumnosDisponibles` setup in `beforeEach`.

## 13. Backend refinements (fixed-professor-views branch — 2026-06-19)

### 13.1 Seed (`backend/seed_dev.py`)
- [x] Added 5 extra ALUMNO users (Pedro Gómez, Laura Díaz, Jorge Silva, Ana Torres, Martín Ruiz) with global vigente Asignacion rol=ALUMNO — not enrolled in any dictado padrón → appear in `alumnos-disponibles` picker.
- [x] Fixed `evaluacion` inserts: added `created_by_id = <profesor_users.id>` so `/profesor/coloquios/mios` returns results. Added a third evaluacion in estado='Cerrada' for dictado1 to give two distinct estados.
- [x] Encuentros already correctly linked to professor's dictados via `dictado_id` (counted in dashboard without `asignacion_id` filter).
- [x] `PROFESOR` now has `("avisos:publicar", True)` in `_MATRIX` (es_propio=True).

### 13.2 RBAC — `avisos:publicar` es_propio=True for PROFESOR (CRÍTICO, approved)
- [x] `seed_dev.py` `_MATRIX`: `("PROFESOR", "avisos:publicar", True)` added.
- [x] `tests/helpers.py` `matrix`: `("PROFESOR", "avisos:publicar", True)` added.
- [x] `app/services/avisos_service.py` `create_aviso`: scope enforcement — PROFESOR (not COORD/ADMIN) may only create POR_MATERIA or POR_COHORTE targeting their own dictados.
- [x] `_resolve_user_context` extended to resolve materia/cohorte from dictado-linked asignaciones (previously only covered direct materia_id/cohorte_id asignaciones).
- [x] New test file `tests/test_avisos/test_profesor_scope.py` (7 tests): propio materia ✅, propio cohorte ✅, GLOBAL ❌ 403, ajena materia ❌ 403, COORDINADOR unaffected ✅.

### 13.3 Per-actividad CSV flow
- [x] **NEW** `GET /api/v1/actividades/{actividad_id}/plantilla-csv` — CSV with header `entrada_padron_id,usuario_id,nombre,apellido,nota,aprobado`, one row per padrón alumno. Gate: `actividades:gestionar` (PROFESOR has). `Content-Disposition: attachment`.
- [x] **NEW** `POST /api/v1/actividades/{actividad_id}/calificaciones-csv` — multipart CSV upload; upserts `Calificacion` per row keyed by `(entrada_padron_id, actividad_id)`. Sets `actividad_id`, `actividad` (=Actividad.nombre), `nota_numerica`, `aprobado`, `origen='Importado'`. Gate: `calificaciones:importar`. Returns `{created, updated, errors, total}`.
- [x] `CalificacionRepository.upsert_for_actividad()` added.
- [x] `ActividadService.generar_plantilla_csv()` and `importar_calificaciones_csv()` added.
- [x] New test file `tests/test_actividades/test_csv_calificaciones.py` (9 tests): template lists alumnos ✅, nota/aprobado empty ✅, 404 on missing actividad ✅, Content-Disposition ✅, upload creates calificaciones ✅, upsert doesn't duplicate ✅, other-tenant 404 ✅, malformed CSV 422 ✅, actividad_id linked ✅.

### 13.4 Comunicado a desaprobados
- [x] Confirmed `GET /profesor/dictados/{id}/atrasados` returns `estado` and `subtipo` ('desaprobado' | 'atrasado_null') — was already implemented; tests added to verify.
- [x] **NEW** `POST /api/v1/profesor/dictados/{dictado_id}/comunicado-atrasados` — accepts `{actividad_id, subtipo: 'desaprobado'|'atrasado_null', asunto_template, cuerpo_template}`. Reuses comunicaciones pipeline (enqueue_masivo). Gate: `comunicacion:enviar`.
- [x] `ProfesorService.prepare_comunicado_atrasados()` added.
- [x] New test file `tests/test_profesor/test_comunicado_atrasados.py` (9 tests): subtipo=desaprobado targets recipients ✅, subtipo=atrasado_null targets faltantes ✅, tenant isolation 404 ✅, sin destinatarios → {total:0, lote_id:null} ✅, subtipo inválido 422 ✅, estado+subtipo fields present ✅.

### Endpoint summary for frontend agent
| Method | Path | Perm | Request | Response |
|--------|------|------|---------|----------|
| GET | `/api/v1/actividades/{id}/plantilla-csv` | `actividades:gestionar` | — | CSV attachment |
| POST | `/api/v1/actividades/{id}/calificaciones-csv` | `calificaciones:importar` | multipart `file` (.csv) | `{created, updated, errors, total}` |
| POST | `/api/v1/profesor/dictados/{id}/comunicado-atrasados` | `comunicacion:enviar` | `{actividad_id, subtipo, asunto_template, cuerpo_template}` | `{total, lote_id}` |

### pytest results: 141/141 passing (test_profesor + test_actividades + test_avisos)
