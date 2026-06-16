## 1. Modelo y Migración

- [x] 1.1 Crear `backend/app/models/comunicacion.py` con modelo `Comunicacion` (id, tenant_id, enviado_por FK→Usuario, materia_id FK→Materia, destinatario cifrado, destinatario_hash, asunto, cuerpo, estado enum, lote_id, enviado_at nullable, reintentos default 0)
- [x] 1.2 Crear migración Alembic `010_create_comunicacion_table.py` con tabla `comunicacion`, índices en `(tenant_id, lote_id)` y `(tenant_id, estado)` (incluye flag tenant.aprobacion_comunicaciones)
- [x] 1.3 Crear `backend/app/schemas/comunicaciones.py` con schemas Pydantic: `ComunicacionRead`, `ComunicacionPreview`, `ComunicacionPreviewRequest`, `ComunicacionEstadoUpdate`, `LoteResumen`, `EnvioMasivoRequest`, `EnvioMasivoItem`, `EnvioMasivoResponse`
- [x] 1.4 Agregar `comunicacion` al `__init__.py` de models

## 2. Máquina de Estados y Plantillas

- [x] 2.1 Implementar `StateMachine` helper en `backend/app/core/state_machine.py` que valide transiciones de `ComunicacionEstado`: Pendiente→Enviando, Pendiente→Cancelado, Enviando→Enviado, Enviando→Error
- [x] 2.2 Implementar `TemplateEngine` helper en `backend/app/core/template_engine.py` con `string.Template` y variables soportadas (`$alumno_nombre`, `$alumno_apellido`, `$materia`, `$docente_nombre`), con validación de variables no reconocidas

## 3. Repository

- [x] 3.1 Crear `backend/app/repositories/comunicacion_repository.py` con `ComunicacionRepository`: create, get_by_id, get_by_lote, get_pendientes (para worker), update_estado, count_by_lote, get_pendientes_count

## 4. Services

- [x] 4.1 Crear `backend/app/services/comunicaciones_service.py` con `ComunicacionesService`: `preview`, `enqueue_masivo`, `aprobar_lote`, `aprobar_individual`, `cancelar_lote`, `cancelar_individual`, `get_estado`, `get_resumen_lote`
- [x] 4.2 Incluir en el service: verificación de permiso `comunicacion:aprobar` en métodos de aprobación, verificación de flag tenant `aprobacion_comunicaciones`, validación de transiciones vía StateMachine, auditoría `COMUNICACION_ENVIAR` al encolar, cifrado de destinatario al crear

## 5. Worker Asíncrono

- [x] 5.1 Crear `backend/workers/comunications_worker.py` con loop asyncio: polling de Pendientes cada N segundos (configurable), transición a Enviando, invocación al transporter, actualización a Enviado/Error, manejo de timeout (5 min → reintento hasta 3), logs estructurados JSON
- [x] 5.2 Agregar entry point en `backend/workers/__main__.py` o script de arranque para ejecutar el worker como proceso independiente

## 6. Routers / API

- [x] 6.1 Crear `backend/app/api/v1/routers/comunicaciones.py` con endpoints:
  - `POST /api/v1/comunicaciones/preview` — preview con sustitución de variables
  - `POST /api/v1/comunicaciones/enviar` — envío masivo (cola)
  - `GET /api/v1/comunicaciones/{id}` — estado individual
  - `GET /api/v1/comunicaciones/lotes/{lote_id}` — resumen de lote
  - `POST /api/v1/comunicaciones/{id}/aprobar` — aprobación individual (`comunicacion:aprobar`)
  - `POST /api/v1/comunicaciones/lotes/{lote_id}/aprobar` — aprobación de lote (`comunicacion:aprobar`)
  - `POST /api/v1/comunicaciones/{id}/cancelar` — cancelación individual (`comunicacion:aprobar`)
  - `POST /api/v1/comunicaciones/lotes/{lote_id}/cancelar` — cancelación de lote (`comunicacion:aprobar`)
- [x] 6.2 Wirear router en `backend/app/main.py` (import + include_router ya existe)

## 7. Permisos

- [x] 7.1 Permisos `comunicacion:enviar` y `comunicacion:aprobar` ya existen pre-seeded en migration 003 (tarea C-04). No requiere nueva migración.
- [x] 7.2 Asignación a roles ya está en el seed de permisos existente. Verificado en test_helpers y seed.py.

## 8. Configuración de Tenant

- [x] 8.1 Agregar columna `aprobacion_comunicaciones` (Boolean, default false) al modelo Tenant
- [x] 8.2 Crear migración para agregar columna a tabla tenant (incluida en migration 010)

## 9. Tests

- [x] 9.1 Crear `backend/tests/test_comunicaciones/test_models.py`: test de creación de Comunicacion, cifrado round-trip de destinatario — ✅ 3 tests passing
- [x] 9.2 Crear `backend/tests/test_comunicaciones/test_state_machine.py`: test de todas las transiciones válidas e inválidas — ✅ 8 tests passing
- [x] 9.3 Crear `backend/tests/test_comunicaciones/test_template_engine.py`: sustitución de variables, variables no soportadas — ✅ 5 tests passing
- [x] 9.4 Crear `backend/tests/test_comunicaciones/test_repository.py`: CRUD, consulta por lote, filtro por tenant — ✅ 13 tests passing
- [x] 9.5 Crear `backend/tests/test_comunicaciones/test_service.py`: preview, enqueue masivo, aprobación lote/individual, cancelación, validación de permisos, tenant flag, auditoría — ✅ 12 tests passing
- [x] 9.6 Crear `backend/tests/test_comunicaciones/test_router.py`: tests de integración contra API (200/403/404/409/422) — ✅ 15+ tests passing
- [x] 9.7 Crear `backend/tests/test_comunicaciones/test_worker.py`: worker procesa Pendiente→Enviado, timeout y reintentos, logs — ✅ 5 tests passing
- [x] 9.8 Ejecutar suite completa de tests y verificar que no se rompen tests existentes — ✅ 661 passed, 0 regressions (3 pre-existing failures confirmed unrelated)
