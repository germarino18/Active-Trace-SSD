## Context

El PROFESOR opera hoy sobre páginas académicas dispersas en `features/academico` (importar calificaciones, monitores, atrasados, comunicación) sin un punto de entrada propio. `frontend/src/pages/DashboardPage.tsx` muestra para PROFESOR estadísticas hardcodeadas ("—"). No existe una vista por materia+cohorte que reúna alumnos, calificaciones, atrasados, equipo, avisos, tareas y coloquios.

Hechos del modelo de datos verificados en el código:

- **"Matemática 2024" es un `Dictado`** (terna materia × carrera × cohorte, ADR-006; `backend/app/models/dictado.py`). Las calificaciones cuelgan de `dictado_id`. Es el ancla del "panel académico de materia y cohorte".
- `Calificacion` (`backend/app/models/calificacion.py`): `entrada_padron_id`, `dictado_id`, `actividad : String(255)`, `nota_numerica`, `nota_textual`, `aprobado : bool`, `origen`. **NO existe una entidad Actividad de primera clase hoy** — una actividad es un string `DISTINCT actividad` por dictado.
- `Evaluacion` es un concepto SEPARADO (coloquios/parciales con cupo + reservas), no "actividad con notas".
- `backend/app/services/analisis/compute.py`: `compute_alumno_atrasado` YA separa `faltantes` (actividad esperada SIN registro = caso null) de `desaprobadas` (registro con nota insuficiente). `compute_metricas_materia` YA devuelve exactamente `{total_alumnos, aprobados, atrasados, total_actividades, promedio_general, sin_datos}`.
- `Asignacion` (`backend/app/models/asignacion.py`) modela el vínculo Usuario × Rol × contexto académico (`dictado_id`/`materia_id`/`carrera_id`/`cohorte_id`) con vigencia derivada por fechas (`desde`/`hasta`); el scope del profesor sale de aquí (rol=PROFESOR, vigente).
- Permisos en `backend/app/core/permissions.py`; calificaciones router tiene preview+importar (`calificaciones:importar`); padron tiene `obtener_padron`, import, sync Moodle, vaciar (`padron:ver`/`padron:importar`/`padron:vaciar`); equipos tiene `/mis-equipos` y `/docentes` (`equipos:asignar`).

Restricciones de proyecto (reglas duras): identidad y `tenant_id` SIEMPRE desde JWT; multi-tenancy row-level filtrado por repositories; RBAC fino `modulo:accion` fail-closed con `require_permission(...)`; Routers→Services→Repositories→Models (sin lógica en routers, sin DB directa en services); soft delete siempre; identidad por UUID interno; ≤500 LOC backend / componentes React <200 LOC; una migración Alembic por cambio de schema; Pydantic `extra='forbid'`; Strict TDD.

## Goals / Non-Goals

**Goals:**
- Vista PROFESOR consolidada: dashboard general con métricas reales + panel por dictado con 6 métricas y tabs.
- Promover `Actividad` a entidad de primera clase de forma ADITIVA y no breaking, habilitando actividades sin notas y `fecha_limite`.
- Definir el concepto de **atrasado-null** (alumno sin `Calificacion` para una Actividad pasada su `fecha_limite`) y disparar comunicado a esos casos.
- Edición individual de calificación, alta/baja individual de alumno, export de plantilla CSV precargada, CRUD de actividad.
- Filtros "míos" (avisos/coloquios emitidos por mí) y equipo docente por dictado COMPARTIDO.
- Reusar al máximo `features/academico` y el pipeline de comunicaciones existente.

**Non-Goals:**
- NO tocar `features/alumno` ni `features/admin` (merge-safety).
- NO migrar el apartado alumno a leer por `actividad_id` (ver "Cambios diferidos").
- NO crear un sistema de actividades para el alumno ni cambiar la `Evaluacion`/coloquios como concepto.
- NO romper ningún flujo existente de importación de calificaciones (sigue poblando `actividad : String`).

## Decisions

### D1 — Actividad como entidad de primera clase, aditiva (aprobado por el usuario)
Crear tabla `Actividad(id, tenant_id, dictado_id, nombre, tipo, fecha_limite + BaseMixin/TenantMixin/soft-delete/audit)`. MANTENER `Calificacion.actividad : String(255)` intacto. AGREGAR `Calificacion.actividad_id : FK → Actividad (nullable)`. Los flujos del profesor pueblan AMBAS columnas (`actividad` string = `Actividad.nombre`, más `actividad_id`). UNA sola migración Alembic, solo aditiva (nueva tabla + columna FK nullable + índice).
- **Por qué**: permite (a) crear actividad sin notas todavía y (b) tener `fecha_limite` para el cálculo atrasado-null, sin tocar el lado alumno que sigue agrupando por el string.
- **Alternativas descartadas**: (1) Reemplazar el string por FK no-nullable → breaking, rompe importación y apartado alumno. (2) Inferir fecha límite fuera del modelo (config por dictado) → no permite fechas por actividad ni actividades sin notas. (3) Reusar `Evaluacion` → semántica distinta (cupo/reservas), contaminaría el dominio.

### D2 — Cálculo de atrasado reutiliza `compute.py`, atrasado-null por `fecha_limite`
La clasificación se apoya en `compute_alumno_atrasado` existente: `faltantes` (sin registro) y `desaprobadas` (registro insuficiente). El refinamiento del profesor: un faltante cuenta como **atrasado-null** sólo si la `Actividad.fecha_limite` ya pasó (`fecha_limite < hoy`). Aprobado = ni faltantes vencidos ni desaprobadas. Atrasado = desaprobado (registro + nota insuficiente) ∪ atrasado-null (faltante vencido).
- **Por qué**: no reinventar la lógica de umbral/aprobación ya testeada; el profesor sólo necesita el eje temporal de `fecha_limite`.
- **Alternativa descartada**: nueva función de atrasados independiente → duplicaría reglas de umbral (RN) y se desincronizaría.

### D3 — Métricas por dictado envuelven `compute_metricas_materia`
El endpoint de métricas por dictado llama al servicio de análisis que ya produce `{total_alumnos, aprobados, atrasados, total_actividades, promedio_general, sin_datos}`. El frontend mapea esos 6 campos al dashboard de 6 métricas.
- **Por qué**: el contrato ya existe y está testeado; sólo falta exponerlo scopeado al dictado.

### D4 — Scope del profesor desde `Asignacion` (rol=PROFESOR, vigente)
El dashboard general y todas las operaciones por dictado derivan los dictados del profesor de `Asignacion` donde `usuario_id = current_user` (de la sesión), `rol = PROFESOR`, vigente por fechas, `tenant_id` de la sesión. Materias asignadas = dictados distintos; alumnos = padrón agregado; encuentros = instancias de esos dictados; atrasados totales = suma de atrasados por dictado.
- **Por qué**: regla dura — identidad SIEMPRE desde JWT, multi-tenancy row-level. Reusa `AsignacionRepository.find_roles_vigentes`.

### D5 — Export de plantilla CSV precargada con el padrón
Endpoint que descarga un `.csv` base con `alumno_id` (entrada_padron_id) + `nombre` + `apellido` del padrón vigente del dictado, con columnas vacías para nota/aprobado/actividad. El profesor lo llena offline y lo sube por el flujo de import existente (preview → importar).
- **Por qué**: reusa el pipeline de importación; minimiza superficie nueva. Sólo lectura del padrón (`obtener_padron` ya existe).

### D6 — RBAC: nuevos permisos finos (CRÍTICO — sólo análisis/propuesta hasta aprobación)
Agregar a `Perm`: `actividades:gestionar` (CRUD actividad), `calificaciones:editar` (PATCH nota+aprobado), `padron:gestionar-alumno` (alta/baja individual). Cada endpoint nuevo declara `require_permission(...)` fail-closed. Seed de roles: PROFESOR (y COORDINADOR/ADMIN) reciben los nuevos permisos.
- **Gobernanza**: RBAC es dominio CRÍTICO. La definición de permisos y su seed NO se implementan sin aprobación humana explícita; las tasks correspondientes quedan marcadas como bloqueadas-en-aprobación.
- **Por qué permisos nuevos y no reusar `calificaciones:importar`**: editar una nota individual y dar de baja un alumno son acciones de mayor impacto y auditoría que importar; merecen permiso propio fail-closed.

### D7 — Comunicado a atrasado-null sobre el pipeline existente (CRÍTICO)
El disparo de comunicado a los atrasado-null usa el pipeline de comunicaciones existente (`comunicaciones` router: preview → enviar_masivo → aprobación). El contenido referencia actividad + materia.
- **Gobernanza**: comunicaciones es dominio CRÍTICO. La generación del comunicado NO se implementa sin aprobación humana; tasks marcadas como bloqueadas-en-aprobación.

### D8 — Equipo docente por dictado COMPARTIDO (capability `equipos` modificada, vía ADDED)
Exponer/ajustar el listado de "compañeros de equipo" del profesor para un dictado dado: otros PROFESOR/TUTOR con `Asignacion` vigente al MISMO `dictado_id` (misma materia+cohorte), no sólo misma materia. Se modela como requirement ADDED en el delta de `equipos` (comportamiento nuevo, sin reescribir requirements existentes para no perder detalle al archivar).
- **Por qué ADDED y no MODIFIED**: las instrucciones recomiendan ADDED cuando se agrega una preocupación nueva sin cambiar comportamiento existente; `/mis-equipos` y `/docentes` siguen igual.

### D9 — Frontend `features/profesor` nuevo + reuso de `features/academico`
Estructura feature-based: `frontend/src/features/profesor/{components,hooks,services,types,pages}`. Reusar `MateriaLayout`, `ImportarCalificacionesPage`, `MonitorSeguimientoPage`, `VistaAtrasadosPage`, `ComunicacionAtrasadosPage`. Hooks de fetch vía TanStack Query, forms con RHF+Zod, Axios centralizado. Componentes <200 LOC, sin `any`, sin class components. Actualizar `DashboardPage.tsx` para consumir el endpoint dashboard-profesor real.

## Risks / Trade-offs

- **[Migración aditiva deja `actividad_id` nullable y calificaciones viejas sin FK]** → Aceptado por diseño: el lado alumno y métricas siguen funcionando por el string `actividad`. Backfill opcional (mapear string→Actividad) queda fuera de alcance; no es requerido para que nada se rompa.
- **[Doble fuente de verdad de la actividad: string + FK]** → Mitigación: los flujos del profesor pueblan SIEMPRE ambas columnas con `actividad = Actividad.nombre`; documentar la invariante y testearla.
- **[Atrasado-null depende de `fecha_limite` cargada]** → Si una actividad no tiene `fecha_limite`, sus faltantes NO se cuentan como atrasado-null (se comportan como hoy). Mitigación: dejar explícito en la spec; sólo las actividades con `fecha_limite` vencida disparan atrasado-null.
- **[Bloqueo por gobernanza CRÍTICA en RBAC y comunicaciones]** → Mitigación: tasks.md separa el trabajo CRÍTICO (permisos nuevos + seed + generación de comunicado) del trabajo autónomo (CRUD/dashboard/métricas/export/edición de UI). Lo CRÍTICO espera firma humana.
- **[Tocar capability `equipos` compartida]** → Mitigación: cambio ADDED, sin reescribir requirements existentes; `features/academico` y `features/admin` no se tocan.
- **[Performance del dashboard general (N dictados → N agregaciones)]** → Mitigación: agregar en el repository con queries scopeadas por tenant; reusar índices `ix_calificacion_tenant_dictado`.

## Migration Plan

1. Crear modelo `Actividad` + columna `Calificacion.actividad_id` (FK nullable) + índice. UNA migración Alembic aditiva.
2. Aplicar la migración (forward sólo crea tabla y columna nullable → seguro). Rollback: drop columna + drop tabla (sin pérdida de datos en `calificacion`).
3. Backend: servicios + endpoints (los CRÍTICOS, sólo tras aprobación de RBAC/comunicaciones).
4. Frontend: `features/profesor` + actualización de `DashboardPage.tsx`.
5. No se requiere backfill; las calificaciones existentes mantienen `actividad_id = NULL` y siguen operando por el string.

## Cambios diferidos — apartado alumno (NO aplicar)

Los siguientes cambios quedan documentados pero **NO se implementan en este change** y **NO generan tasks**. El enfoque aditivo (D1) garantiza que el apartado alumno siga funcional leyendo el string `actividad`:

- `backend/app/services/alumno_service.py` + `backend/app/schemas/alumno.py`: migrar de agrupar por `actividad` string a leer por `actividad_id`; exponer `fecha_limite` y el estado atrasado-null al alumno.
- `frontend/src/features/alumno/pages/MateriaDetallePage.tsx`: mostrar la fecha límite y el estado "no entregado a tiempo".

Estos deben permanecer funcionales con el enfoque aditivo (siguen leyendo el string `actividad`); su migración a `actividad_id` se planificará en un change futuro.

## Open Questions

- ¿El comunicado a atrasado-null debe agruparse por actividad o por alumno (un mensaje con todas sus actividades vencidas)? — a confirmar en la fase CRÍTICA con aprobación humana.
- ¿`Actividad.tipo` es un enum cerrado (TP/Parcial/Final/Otro) o string libre? — se asume string acotado por la UI; confirmar al implementar el CRUD.
