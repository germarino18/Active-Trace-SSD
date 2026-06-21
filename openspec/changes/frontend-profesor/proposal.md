## Why

El rol PROFESOR no tiene una vista consolidada propia: el dashboard general muestra estadísticas hardcodeadas ("—") y no existe un panel por materia+cohorte (Dictado) que le permita gestionar alumnos, calificaciones, atrasados, equipo docente, avisos, tareas y coloquios desde un solo lugar. Hoy el profesor depende de páginas académicas dispersas (`features/academico`) sin un punto de entrada coherente ni métricas reales. Este change cierra ese hueco: completa el flujo central del PROFESOR (importar → analizar → comunicar) sobre datos reales, scopeado a sus dictados asignados.

Además, el modelo de actividades es hoy implícito: una "actividad" es solo un string `DISTINCT actividad` colgado de las calificaciones. Esto impide al profesor (a) crear una actividad sin notas todavía, y (b) definir una fecha límite que habilite el concepto de **atrasado-null** (alumno sin registro de calificación una vez pasada la fecha de entrega). Promover `Actividad` a entidad de primera clase de forma aditiva desbloquea ambos casos sin romper el apartado alumno existente.

## What Changes

### Modelo de datos (aditivo, no breaking)
- **NUEVA** tabla `Actividad(id, tenant_id, dictado_id, nombre, tipo, fecha_limite + soft-delete/audit mixins)`.
- **SE MANTIENE** `Calificacion.actividad : String(255)` intacto (el apartado alumno sigue leyendo el string).
- **SE AGREGA** `Calificacion.actividad_id : FK → Actividad (nullable)`. Los flujos del profesor poblarán AMBAS columnas.
- UNA sola migración Alembic, solo aditiva.

### Backend (endpoints/servicios a AGREGAR)
- Endpoint agregado **dashboard-profesor**: materias asignadas, alumnos, encuentros, atrasados totales — scopeado a los dictados del profesor (vía `Asignacion` rol=PROFESOR vigente).
- Endpoint **métricas por dictado** envolviendo el `compute_metricas_materia` existente.
- **PATCH calificación individual** (editar `nota` + `aprobado`). **CRÍTICO** — nuevo permiso RBAC.
- **Export CSV plantilla**: descarga base con `alumno_id + nombre + apellido` del padrón del dictado para llenar offline y subir vía import existente.
- **Alta/baja individual de alumno** en un dictado. **CRÍTICO** — nuevos permisos RBAC.
- **CRUD Actividad** por dictado (crear sin notas, listar, editar fecha_limite, soft-delete). **CRÍTICO** — nuevos permisos RBAC.
- Filtros **"mías"**: avisos emitidos por mí (`created_by`), coloquios/evaluaciones emitidas por mí.
- Filtro de **equipo docente por dictado COMPARTIDO** (misma materia+cohorte), no solo por materia.

### Frontend (`features/profesor` NUEVO + reuso de `features/academico`)
- Dashboard general PROFESOR con stats reales (hoy hardcodeadas en `DashboardPage.tsx`).
- Panel materia+cohorte (Dictado): dashboard de 6 métricas + tabs (Alumnos CRUD, Calificaciones/Actividades, Atrasados, Equipo docente, Avisos míos, Mis tareas, Mis coloquios).
- Vista de atrasados que distingue **Aprobado** vs **Atrasado**, y dentro de atrasado: **desaprobado** (registro + nota insuficiente) vs **atrasado-null** (sin registro pasada la `fecha_limite`). Los atrasado-null → generar comunicado (actividad + materia). **CRÍTICO**.

### Fuera de alcance (merge-safety)
- NO se toca `features/alumno` ni `features/admin`.

## Capabilities

### New Capabilities
- `profesor-dashboard`: Vista consolidada del PROFESOR — dashboard general con métricas reales scopeadas a dictados asignados, y panel por dictado (materia+cohorte) con sus 6 métricas y navegación a tabs.
- `actividades-crud`: Actividad como entidad de primera clase por dictado — crear sin notas, listar, editar `fecha_limite`, soft-delete; base para el cálculo de atrasado-null.
- `calificacion-edicion`: Edición individual de calificación (nota + aprobado) por el profesor, con permiso RBAC dedicado y auditoría.
- `gestion-alumnos-dictado`: Alta/baja individual de alumno en un dictado y export de plantilla CSV precargada con el padrón para carga offline.
- `atrasados-profesor`: Clasificación de alumnos en Aprobado / Atrasado, distinguiendo desaprobado vs atrasado-null (basado en `fecha_limite`), y disparo de comunicado a los atrasado-null.

### Modified Capabilities
- `equipos`: El filtro de equipo docente pasa a considerar el dictado COMPARTIDO (misma materia+cohorte) — otros PROFESOR/TUTOR con `Asignacion` al mismo dictado — en vez de solo la materia.

## Impact

- **Modelos/migración**: `backend/app/models/calificacion.py` (FK aditiva), nuevo `backend/app/models/actividad.py`, una migración Alembic.
- **RBAC**: nuevos permisos en `backend/app/core/permissions.py` (`actividades:gestionar`, `calificaciones:editar`, `padron:gestionar-alumno`) y su seed de roles — dominio **CRÍTICO**, requiere aprobación humana.
- **Backend**: nuevos endpoints en routers `analisis`/`calificaciones`/`padron`/`equipos` (+ posible router `actividades`), servicios correspondientes (`analisis`, `calificaciones`, `padron`, `equipo_service`), reutilizando `compute_metricas_materia` y `compute_alumno_atrasado`.
- **Comunicaciones**: disparo de comunicado para atrasado-null sobre el pipeline existente (`comunicaciones` router: preview → enviar_masivo → aprobación) — dominio **CRÍTICO**, requiere aprobación humana.
- **Frontend**: nuevo `frontend/src/features/profesor/{components,hooks,services,types,pages}`; reuso de `MateriaLayout`, `ImportarCalificacionesPage`, `MonitorSeguimientoPage`, `VistaAtrasadosPage`, `ComunicacionAtrasadosPage` de `features/academico`; actualización de `frontend/src/pages/DashboardPage.tsx` para stats reales del PROFESOR.
- **Sin tocar**: `features/alumno`, `features/admin`. El apartado alumno permanece funcional gracias al enfoque aditivo.
