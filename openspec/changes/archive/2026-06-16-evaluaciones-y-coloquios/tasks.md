## 1. Modelos y Migración

- [x] 1.1 Crear modelo `Evaluacion` en `app/models/evaluacion.py` con: `dictado_id` (FK → Dictado), `tipo` (enum: Parcial | TP | Coloquio | Recuperatorio), `instancia` (texto), `dias_disponibles` (entero), `cupo_maximo` (entero), `estado` (Activa | Cerrada). Heredar de `BaseMixin`, `TenantMixin`, `AuditMixin`, `Base`.
- [x] 1.2 Crear modelo `ReservaEvaluacion` en `app/models/reserva_evaluacion.py` con: `evaluacion_id` (FK → Evaluacion), `alumno_id` (FK → Usuario), `fecha_hora` (timestamp), `estado` (Activa | Cancelada). Unique constraint `(evaluacion_id, alumno_id)` donde estado = Activa.
- [x] 1.3 Crear modelo `ResultadoEvaluacion` en `app/models/resultado_evaluacion.py` con: `evaluacion_id` (FK → Evaluacion), `alumno_id` (FK → Usuario), `nota_final` (texto). Unique constraint `(evaluacion_id, alumno_id)`.
- [x] 1.4 Agregar `AlumnoConvocado` como tabla intermedia (FK → Evaluacion + FK → Usuario) o modelar como lista implícita vía `ReservaEvaluacion`. Según spec: importar alumnos es independiente de reservar, así que crear modelo `AlumnoConvocado` en `app/models/alumno_convocado.py` con unique `(evaluacion_id, alumno_id)`.
- [x] 1.5 Crear migración Alembic `00N_evaluaciones_coloquios` con las tablas `evaluacion`, `reserva_evaluacion`, `resultado_evaluacion`, `alumno_convocado`, índices compuestos por tenant, y FK a dictado con CASCADE.
- [x] 1.6 Agregar códigos de auditoría `COLOQUIO_CREAR`, `COLOQUIO_IMPORTAR_ALUMNOS`, `COLOQUIO_RESERVAR`, `COLOQUIO_CANCELAR_RESERVA`, `COLOQUIO_REGISTRAR_RESULTADO`, `COLOQUIO_CERRAR` en `app/core/acciones_auditoria.py`.
- [x] 1.7 Sembrar permisos `coloquios:gestionar` (COORDINADOR, ADMIN), `coloquios:reservar` (ALUMNO), `coloquios:ver` (COORDINADOR, ADMIN, PROFESOR) en el seed de permisos.

## 2. Schemas Pydantic

- [x] 2.1 Crear `app/schemas/coloquios.py` con: `EvaluacionCreate`, `EvaluacionRead`, `EvaluacionUpdate`, `ReservaEvaluacionCreate`, `ReservaEvaluacionRead`, `ResultadoEvaluacionCreate`, `ResultadoEvaluacionRead`, `AlumnoConvocadoCreate`, `AlumnoConvocadoRead`, `MetricasColoquiosRead`. Todos con `extra='forbid'`; `Read` con `from_attributes=True`.

## 3. Repositorios

- [x] 3.1 Crear `EvaluacionRepository` en `app/repositories/evaluacion_repository.py` con métodos: `list_by_tenant(filters)`, `get_by_id`, `create`, `update`, `count_metricas()`.
- [x] 3.2 Crear `ReservaEvaluacionRepository` en `app/repositories/reserva_evaluacion_repository.py` con: `create` (con FOR UPDATE), `cancelar`, `list_activas_by_tenant(filters)`, `count_activas_by_evaluacion`.
- [x] 3.3 Crear `ResultadoEvaluacionRepository` en `app/repositories/resultado_evaluacion_repository.py` con: `create`, `list_by_tenant(filters)`, `get_by_evaluacion_alumno`.
- [x] 3.4 Crear `AlumnoConvocadoRepository` en `app/repositories/alumno_convocado_repository.py` con: `bulk_import(idempotent)`, `list_by_evaluacion`, `exists(evaluacion_id, alumno_id)`.

## 4. Servicios

- [x] 4.1 Crear `ColoquioService` en `app/services/coloquios/__init__.py` con factory method `create(cls, session, tenant_id)`, métodos para ABM de evaluaciones, importar alumnos, panel de métricas, registro académico consolidado.
- [x] 4.2 Crear `ReservaService` en `app/services/coloquios/reserva_service.py` con lógica de: reservar (verificar habilitación, cupo con FOR UPDATE, crear reserva), cancelar (verificar titularidad o permiso gestionar), listar agenda.
- [x] 4.3 Crear `ResultadoService` en `app/services/coloquios/resultado_service.py` con: registrar resultado (verificar alumno convocado, único resultado), consultar registro académico consolidado.

## 5. Routers (Endpoints)

- [x] 5.1 Crear `app/api/v1/routers/coloquios.py` con router `prefix="/api/v1/coloquios"`, tag="Coloquios", dependencias `[Depends(get_current_user)]`. Endpoints de gestión (`coloquios:gestionar`): POST (crear), PATCH (editar), POST /{id}/cerrar, POST /{id}/importar-alumnos, GET /metricas.
- [x] 5.2 Endpoints de reserva (`coloquios:reservar`): POST /{id}/reservar, POST /reservas/{id}/cancelar.
- [x] 5.3 Endpoints de resultados (`coloquios:gestionar`): POST /{id}/resultados.
- [x] 5.4 Endpoints de consulta (`coloquios:ver`): GET (lista convocatorias), GET /{id} (detalle), GET /reservas (agenda), GET /resultados (registro académico).
- [x] 5.5 Registrar los routers en `app/app.py` (o donde se registren los routers existentes).

## 6. Tests

- [x] 6.1 Crear `tests/test_coloquios/__init__.py` (vacío) y `tests/test_coloquios/conftest.py` con fixtures: `make_token`, `seeded_tenant`, usuarios con roles (coordinador, profesor, alumno), `dictado_valido`, `evaluacion_valida`.
- [x] 6.2 Crear `tests/test_coloquios/test_models.py`: tests de creación de Evaluacion, ReservaEvaluacion, ResultadoEvaluacion, AlumnoConvocado; defaults; unicidad; aislamiento multi-tenant.
- [x] 6.3 Crear `tests/test_coloquios/test_repository.py`: tests CRUD de cada repositorio; listado con filtros; conteo de métricas; FOR UPDATE en reserva.
- [x] 6.4 Crear `tests/test_coloquios/test_service.py`: tests de lógica de negocio (reserva con/sin cupo, importación idempotente, cancelación, registro único de resultado, métricas).
- [x] 6.5 Crear `tests/test_coloquios/test_router.py`: tests de endpoints vía HTTP client — creación, listado, reserva, cancelación, registro resultado, RBAC 403/200, aislamiento multi-tenant, auditoría.
