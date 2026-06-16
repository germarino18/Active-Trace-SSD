## 1. Scaffolding y permisos

- [x] 1.1 Crear estructura `app/modules/analisis/` con `__init__.py`, `routers/`, `services/`, `schemas/`
- [x] 1.2 Registrar permiso `atrasados:ver` en la matriz RBAC (seed o migración)
- [x] 1.3 Wirear router de analisis en la aplicación FastAPI

## 2. Funciones de cómputo puro (testables sin DB)

- [x] 2.1 Implementar `compute_alumno_atrasado(calificaciones, umbral) -> bool` según RN-06 (actividades faltantes O nota < umbral)
- [x] 2.2 Implementar `compute_ranking_aprobadas(calificaciones, umbral) -> list[dict]` según RN-09 (solo alumnos con ≥1 aprobada, orden descendente)
- [x] 2.3 Implementar `compute_nota_final(calificaciones, actividades_configuradas) -> float | None` (promedio simple de notas numéricas)
- [x] 2.4 Implementar `detect_tps_sin_corregir(finalizaciones, calificaciones) -> list[dict]` según RN-07/08 (cruce, solo textuales)
- [x] 2.5 Implementar `compute_metricas_materia(calificaciones, umbral) -> dict` (total_alumnos, aprobados, atrasados, total_actividades, promedio_general)
- [x] 2.6 Implementar `resolve_umbral(unbral_materia: UmbralMateria | None) -> UmbralDefaults` (default 60% y valores aprobatorios por defecto)

## 3. AnalisisService

- [x] 3.1 Implementar `AnalisisService.get_alumnos_atrasados(tenant_id, materia_id, usuario)` con consulta a CalificacionRepository + UmbralMateriaRepository
- [x] 3.2 Implementar `AnalisisService.get_ranking_aprobadas(tenant_id, materia_id)` aplicando `compute_ranking_aprobadas`
- [x] 3.3 Implementar `AnalisisService.get_reporte_materia(tenant_id, materia_id)` aplicando `compute_metricas_materia`
- [x] 3.4 Implementar `AnalisisService.get_notas_finales(tenant_id, materia_id, actividades_configuradas)` aplicando `compute_nota_final`
- [x] 3.5 Implementar `AnalisisService.get_tps_sin_corregir(tenant_id, materia_id, finalizaciones)` aplicando `detect_tps_sin_corregir`, con error si no hay finalizaciones
- [x] 3.6 Implementar `AnalisisService.get_monitor_general(tenant_id, filtros)` para COORDINADOR/ADMIN con filtros materia, regional, comisión, q, estado
- [x] 3.7 Implementar `AnalisisService.get_monitor_seguimiento(tenant_id, usuario_id, filtros, fecha_desde, fecha_hasta)` con scope por asignaciones vigentes y rango de fechas opcional
- [x] 3.8 Integrar paginación (offset/limit con default 50, max 200, total_count) en todos los métodos de monitor

## 4. Pydantic schemas

- [x] 4.1 Crear schemas de request: `AtrasadosQuery`, `RankingQuery`, `ReporteQuery`, `MonitorGeneralQuery`, `MonitorSeguimientoQuery` con `extra='forbid'`
- [x] 4.2 Crear schemas de response: `AlumnoAtrasado`, `RankingItem`, `ReporteMateria`, `NotaFinalAlumno`, `TPSinCorregir`, `MonitorItem`, `MonitorPaginado`
- [x] 4.3 Agregar validación de rango de fechas (desde <= hasta) en MonitorSeguimientoQuery

## 5. Endpoints REST

- [x] 5.1 Implementar `GET /api/admin/analisis/atrasados` con gating `atrasados:ver` y filtro dictado_id
- [x] 5.2 Implementar `GET /api/admin/analisis/ranking` con gating `atrasados:ver` y filtro dictado_id
- [x] 5.3 Implementar `GET /api/admin/analisis/reportes/materia/{dictado_id}` con gating `atrasados:ver`
- [x] 5.4 Implementar `GET /api/admin/analisis/notas-finales` con gating `atrasados:ver` y filtro dictado_id
- [x] 5.5 Implementar `GET /api/admin/analisis/tps-sin-corregir/export` con gating `atrasados:ver`, filtro dictado_id, error 400 si no hay finalizaciones
- [x] 5.6 Implementar `GET /api/admin/analisis/monitor/general` con gating `atrasados:ver` + verificación rol COORDINADOR/ADMIN
- [x] 5.7 Implementar `GET /api/admin/analisis/monitor/seguimiento` con gating `atrasados:ver` y parámetros de fecha opcionales

## 6. Tests

- [x] 6.1 Escribir tests unitarios para TODAS las funciones de cómputo puro (2.1-2.6) — al menos 3 escenarios por función
- [x] 6.2 Escribir tests de integración para `AnalisisService` con base real (DB de test) — un escenario feliz y uno edge por método
- [x] 6.3 Escribir tests de integración para endpoints (cliente FastAPI de test) — 200, 403 por endpoint
- [x] 6.4 Verificar cobertura ≥80% líneas y ≥90% reglas de negocio (RN-06 a RN-09)

## 7. Auditoría

- [x] 7.1 Registrar eventos de auditoría `ANALISIS_ATRASADOS_CONSULTA`, `ANALISIS_RANKING_CONSULTA`, `ANALISIS_REPORTE_CONSULTA`, `ANALISIS_NOTAS_CONSULTA`, `ANALISIS_TPS_CONSULTA`, `ANALISIS_MONITOR_CONSULTA`
- [x] 7.2 Integrar audit-log en cada método de AnalisisService antes de retornar
