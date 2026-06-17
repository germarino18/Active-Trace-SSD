## 1. Schemas y Capa de Presentación

- [x] 1.1 Crear `backend/app/schemas/auditoria.py` con schemas Pydantic: `AccionesPorDiaItem`, `ComunicacionesPorDocenteItem`, `InteraccionesPorDocenteMateriaItem`, `UltimasAccionesResponse`, `LogAuditoriaItem`, `LogAuditoriaPaginado` (con `total`, `offset`, `limit`, `items`), parámetros de filtro combinados (fecha_desde, fecha_hasta, materia_id, usuario_id, accion, limit, offset)
- [x] 1.2 Activar `extra='forbid'` en todos los schemas vía `model_config = ConfigDict(extra='forbid')`

## 2. AuditoriaService

- [x] 2.1 Crear `backend/app/services/auditoria_service.py` con `AuditoriaService` que implemente:
  - `get_acciones_por_dia(tenant_id, fecha_desde, fecha_hasta, usuario_id, materia_id)` — GROUP BY fecha sobre AuditLog
  - `get_comunicaciones_por_docente(tenant_id, fecha_desde, fecha_hasta)` — agregación de estados de Comunicacion por docente y materia
  - `get_interacciones_por_docente_materia(tenant_id, fecha_desde, fecha_hasta)` — desglose por código de acción
  - `get_ultimas_acciones(tenant_id, limit, fecha_desde, fecha_hasta, materia_id, usuario_id)` — log detallado con límite configurable (max 1000)
  - `get_log_auditoria(tenant_id, offset, limit, fecha_desde, fecha_hasta, materia_id, usuario_id, accion)` — log completo paginado con filtros combinados
- [x] 2.2 Implementar scope `(propio)` para COORDINADOR: los métodos aceptan `user_id` y `roles` y filtran `actor_id` contra asignaciones supervisadas si el rol es COORDINADOR; ADMIN y FINANZAS ven todo
- [x] 2.3 Resolver nombres de actor y materia en los resultados (join contra Usuario y Materia para incluir `actor_nombre` y `materia_nombre`)

## 3. Router Auditoría

- [x] 3.1 Crear `backend/app/api/v1/routers/auditoria.py` con endpoints:
  - `GET /api/v1/auditoria/acciones-por-dia` — guard `auditoria:ver`
  - `GET /api/v1/auditoria/comunicaciones-por-docente` — guard `auditoria:ver`
  - `GET /api/v1/auditoria/interacciones-por-docente-materia` — guard `auditoria:ver`
  - `GET /api/v1/auditoria/ultimas-acciones` — guard `auditoria:ver`
  - `GET /api/v1/auditoria/log` — guard `auditoria:ver`, paginado con offset/limit
- [x] 3.2 Todos los endpoints SOLO aceptan GET — cualquier otro método responde 405
- [x] 3.3 Wirear router en `backend/app/main.py` (import + include_router)

## 4. Permisos

- [x] 4.1 Verificar que el permiso `auditoria:ver` ya existe en el seed (C-04/C-05) — ✅ confirmado en `backend/app/core/permissions.py` línea 21: `Perm.AUDITORIA_VER = "auditoria:ver"`
- [x] 4.2 Verificar asignación del permiso en la matriz de roles: ADMIN, COORDINADOR `(propio)`, FINANZAS — ✅ confirmado en `knowledge-base/03_actores_y_roles.md` línea 84

## 5. Tests

- [x] 5.1 Crear `backend/tests/test_auditoria/__init__.py`
- [x] 5.2 Crear `backend/tests/test_auditoria/conftest.py` con fixtures de AuditLog, Comunicacion y Asignacion
- [x] 5.3 Crear `backend/tests/test_auditoria/test_schemas.py`: validación de schemas, `extra='forbid'`, filtros combinados
- [x] 5.4 Crear `backend/tests/test_auditoria/test_service.py`: agregaciones por día, comunicaciones por docente, interacciones, últimas acciones con límite, log paginado, scope `(propio)` de COORDINADOR, tenant isolation
- [x] 5.5 Crear `backend/tests/test_auditoria/test_router.py`: tests de integración — GET 200 con datos, GET 200 sin datos, 403 sin permiso, 405 en POST/PUT/DELETE, filtros combinados, paginación, límite máximo 1000
- [x] 5.6 Ejecutar suite completa de tests y verificar que no se rompen tests existentes
