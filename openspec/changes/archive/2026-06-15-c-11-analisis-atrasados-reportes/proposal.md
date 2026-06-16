## Why

Hasta ahora el sistema importa calificaciones (C-10) y permite configurar umbrales de aprobación, pero no ofrece visibilidad del estado académico de los alumnos. Sin análisis ni reportes, los docentes no pueden detectar alumnos en riesgo, priorizar correcciones ni dar seguimiento. Este cambio incorpora la capa de análisis y monitoreo que transforma los datos crudos en información accionable para TUTOR, PROFESOR, COORDINADOR y ADMIN.

## What Changes

- Nuevo `AnalisisService` con métodos de consulta y cómputo sobre `Calificacion` y `UmbralMateria` existentes (sin nuevas tablas ni migraciones)
- Endpoints GET para cada funcionalidad, gated por permiso `atrasados:ver`
- Lógica de detección de alumnos atrasados (RN-06): actividades faltantes O nota < umbral
- Ranking de actividades aprobadas (RN-09): solo alumnos con ≥1 aprobada, orden descendente
- Reportes rápidos por materia con métricas consolidadas (total alumnos, aprobados, atrasados, actividades)
- Cálculo de nota final agrupada por alumno a partir de actividades configuradas
- Exportación de TPs sin corregir (RN-07/08): cruce contra reporte de finalización LMS, solo actividades textuales
- Monitor general (COORDINADOR/ADMIN): vista transversal con filtros (materia, regional, comisión, alumno, estado)
- Monitor seguimiento (TUTOR/PROFESOR): vista filtrable de alumnos asignados
- Monitor seguimiento (COORDINADOR/ADMIN): extiende el anterior con rango de fechas
- Todos los endpoints registran auditoría vía audit-log existente

## Capabilities

### New Capabilities
- `analisis-atrasados`: Detección de alumnos atrasados (F2.2, RN-06) y ranking de actividades aprobadas (F2.3, RN-09). Endpoints GET con filtros por materia.
- `reportes-rapidos`: Reportes consolidados por materia con métricas clave (F2.4) y cálculo de nota final agrupada por alumno (F2.5).
- `exportar-tps-pendientes`: Exportación de TPs sin corregir (F2.6, RN-07/08). Cruce contra finalización LMS, solo actividades textuales. Archivo descargable.
- `monitor-academico`: Monitores de seguimiento académico — vista general para COORDINADOR/ADMIN con filtros transversales (F2.7) y vista de seguimiento para TUTOR/PROFESOR (F2.8) con extensión de rango de fechas para COORDINADOR/ADMIN (F2.9).

### Modified Capabilities
<!-- No existing specs change behavior — todo es nueva funcionalidad query-based sobre Calificacion + UmbralMateria existentes -->

## Impact

- **Nuevo backend module**: `app/modules/analisis/` con routers, services, schemas
- **Nuevos endpoints**: ~8-10 GET endpoints bajo `/api/v1/analisis/`
- **Nuevo permiso**: `atrasados:ver` agregado a la matriz RBAC
- **Sin nuevos modelos DB** — todo es query-based sobre `Calificacion` y `UmbralMateria`
- **Sin migraciones** — no se altera el schema
- **Dependencias**: C-10 (Calificacion + UmbralMateria models and repos), C-07 (asignaciones vigentes), auditoría (C-05)
- **Frontend**: nuevas páginas/pantallas de monitoreo y reportes (futuro change)
