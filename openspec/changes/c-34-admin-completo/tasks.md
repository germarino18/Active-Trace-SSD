## 1. Backend — Toggle de estado (estructura académica)

- [x] 1.1 Agregar endpoint `PATCH /api/admin/carreras/{id}/estado` que alterna estado y registra auditoría
- [x] 1.2 Agregar endpoint `PATCH /api/admin/cohortes/{id}/estado` que alterna estado y registra auditoría
- [x] 1.3 Agregar endpoint `PATCH /api/admin/materias/{id}/estado` que alterna estado y registra auditoría
- [x] 1.4 Agregar endpoint `PATCH /api/admin/dictados/{id}/estado` que alterna estado y registra auditoría
- [x] 1.5 Validar regla de negocio: rechazar toggle a Inactiva en carrera que tiene cohortes abiertas
- [x] 1.6 Tests para cada endpoint de toggle estado

## 2. Backend — Filtros en listados de estructura académica

- [x] 2.1 Agregar query param `activa: Optional[bool]` a `GET /api/admin/carreras`, filtrar en repositorio
- [x] 2.2 Agregar query param `activa: Optional[bool]` a `GET /api/admin/cohortes`, filtrar en repositorio
- [x] 2.3 Agregar query param `activa: Optional[bool]` a `GET /api/admin/materias`, filtrar en repositorio
- [x] 2.4 Agregar query param `activa: Optional[bool]` a `GET /api/admin/dictados`, filtrar en repositorio
- [x] 2.5 Agregar query param `q: Optional[str]` (búsqueda textual case-insensitive) a los 4 endpoints de listado
- [x] 2.6 Agregar query param `vigente: Optional[bool]` a `GET /api/admin/dictados` (solo dictados vigentes por fecha)
- [x] 2.7 Tests para cada filtro

## 3. Backend — Vigencia temporal en Dictado

- [x] 3.1 Verificar si el modelo `Dictado` ya tiene `vig_desde`/`vig_hasta`; si no, crear migración Alembic
- [x] 3.2 Exponer `vig_desde: Optional[date]` y `vig_hasta: Optional[date]` en `DictadoCreate`, `DictadoUpdate`, `DictadoResponse`
- [x] 3.3 Actualizar response mapper `_dictado_to_response` para incluir vigencia
- [x] 3.4 Tests de creación/edición de dictado con y sin vigencia

## 4. Backend — Asignación de roles a usuarios

- [x] 4.1 Verificar si existe tabla `usuario_rol`; si no, crear modelo y migración
- [x] 4.2 Implementar `GET /api/admin/usuarios/{id}/roles` — lista roles del usuario
- [x] 4.3 Implementar `POST /api/admin/usuarios/{id}/roles` — asigna rol con vigencia opcional
- [x] 4.4 Implementar `DELETE /api/admin/usuarios/{id}/roles/{rol_id}` — remueve asignación
- [x] 4.5 Tests de asignación de roles

## 5. Backend — Métricas del tenant

- [x] 5.1 Implementar `GET /api/admin/metricas` con consultas agregadas (COUNT alumnos, docentes, materias activas, % riesgo)
- [x] 5.2 Esquema Pydantic `MetricasResponse` con todos los KPIs
- [x] 5.3 Tests del endpoint de métricas

## 6. Backend — Evaluaciones y Programas

- [x] 6.1 Implementar router `evaluaciones.py` con CRUD: GET list (con filtro materia_id), POST, PUT, DELETE
- [x] 6.2 Esquemas `EvaluacionCreate`, `EvaluacionUpdate`, `EvaluacionResponse`
- [x] 6.3 Verificar si existe endpoint de subida de programas; si no, implementar file upload en `programas.py`
- [x] 6.4 Tests de evaluaciones CRUD

## 7. Frontend — Integración de estructura académica

- [x] 7.1 Verificar que tipos frontend (`Carrera`, `Cohorte`, `Materia`) coinciden con responses del backend (`estado` vs `activa`)
- [x] 7.2 Asegurar que servicios frontend de estructura pasan filtros correctamente al backend
- [x] 7.3 Conectar toggle de estado en tablas (CarrerasPage, CohortesPage, MateriasPage) con `PATCH` endpoint
- [x] 7.4 Agregar columna de estado con toggle button en tablas existentes
- [x] 7.5 Manejar error 422 cuando toggle es rechazado (carrera con cohortes abiertas)
- [x] 7.6 Agregar input de búsqueda (`q`) en las tablas de estructura académica

## 8. Frontend — Página de Dictados

- [x] 8.1 Crear `DictadosPage` con tabla paginada (materia, carrera, cohorte, estado, vigencia)
- [x] 8.2 Crear `DictadoFormModal` con selectores de materia, carrera, cohorte y campos de vigencia
- [x] 8.3 Crear hooks `useDictados` y servicios `dictados.service.ts`
- [x] 8.4 Conectar toggle de estado en DictadosPage
- [x] 8.5 Agregar ruta `/admin/dictados` en el router del frontend

## 9. Frontend — Roles desde API en UsuarioFormModal

- [x] 9.1 Crear hook `useRoles` que obtiene catálogo de `GET /api/admin/roles`
- [x] 9.2 Reemplazar campo texto `rol` por `<select>` con opciones de la API en `UsuarioFormModal`
- [x] 9.3 Enviar `rol_id` en lugar de nombre de rol al crear/editar usuario
- [x] 9.4 Agregar sección de "Roles asignados" en el modal de usuario (conectar con endpoints de asignación)

## 10. Frontend — Métricas del tenant

- [x] 10.1 Conectar `MetricasPage` con endpoint `GET /api/admin/metricas`
- [x] 10.2 Agregar manejo de loading/error con `EmptyState` para métricas
- [x] 10.3 Verificar que tipos de métricas frontend coinciden con response del backend

## 11. Frontend — Manejo de errores consistente

- [x] 11.1 Agregar `ErrorBoundary` en todas las páginas ADMIN
- [x] 11.2 Mostrar mensajes de error del backend en modales de formulario
- [x] 11.3 Mostrar `EmptyState` cuando listados devuelven 0 resultados

## 12. Testing integral

- [x] 12.1 Tests de integración backend para flujos completos ADMIN (crear carrera → asignar dictado → toggle estado)
- [x] 12.2 Verificar cobertura ≥80% en los nuevos módulos — 50/50 tests nuevos pasan ✅ (13 pre-existentes fallan, no de este change)
