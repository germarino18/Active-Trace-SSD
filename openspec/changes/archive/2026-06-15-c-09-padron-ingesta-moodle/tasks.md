## 1. Models y Migración

- [x] 1.1 Crear `VersionPadron` model en `backend/app/models/version_padron.py` con BaseMixin, TenantMixin, dictado_id FK, cargado_por FK, activa boolean default true, cargado_at DateTime
- [x] 1.2 Crear `EntradaPadron` model en `backend/app/models/entrada_padron.py` con BaseMixin, TenantMixin, version_id FK, usuario_id FK nullable, nombre, apellidos, email cifrado AES-256, comision, regional
- [x] 1.3 Registrar ambos modelos en `backend/app/models/__init__.py`
- [x] 1.4 Generar migración Alembic 008 con tablas `version_padron` y `entrada_padron`, índices por (tenant_id, dictado_id), (tenant_id, version_id), y unique partial index `activa=true` por dictado_id
- [x] 1.5 Escribir test de migración: verificar que las tablas se crean con las columnas esperadas

## 2. Permisos RBAC y Action Codes

- [x] 2.1 Agregar `PADRON_IMPORTAR`, `PADRON_VACIAR`, `PADRON_VER` en `backend/app/core/permissions.py`
- [x] 2.2 Agregar `PADRON_VACIAR` en el catálogo de action codes de auditoría
- [x] 2.3 Escribir test que verifique que los nuevos permisos existen como constantes en `Perm`

## 3. Repositorios

- [x] 3.1 Crear `VersionPadronRepository` en `backend/app/repositories/version_padron_repository.py` con métodos: `create`, `find_active_by_dictado`, `find_by_id`, `find_by_dictado`, `deactivate_version`, `delete_by_dictado_and_cargador`, `delete_all_by_dictado`
- [x] 3.2 Crear `EntradaPadronRepository` en `backend/app/repositories/entrada_padron_repository.py` con métodos: `bulk_create`, `find_by_version`, `count_by_version`, `delete_by_version`
- [x] 3.3 Escribir tests de repositorios: CRUD básico, activar/desactivar versión, bulk_create entradas, aislamiento tenant

## 4. Schemas Pydantic

- [x] 4.1 Crear `backend/app/schemas/padron.py` con DTOs: `VersionPadronResponse`, `EntradaPadronResponse`, `PadronPreviewRequest`, `PadronPreviewResponse`, `PadronImportConfirm`, `PadronImportResponse`, `VaciarResponse`, `VersionPadronHistoryResponse` (todos con `extra='forbid'`)
- [x] 4.2 Escribir tests de schemas: validación de campos requeridos, rechazo de campos extra, tipos correctos

## 5. Servicio de Padrón

- [x] 5.1 Crear `backend/app/services/padron/__init__.py`
- [x] 5.2 Implementar `PadronService` en `backend/app/services/padron/padron_service.py` con métodos:
  - `preview_archivo(file, dictado_id)`: parsea xlsx/csv, valida columnas, genera token de preview
  - `confirmar_importacion(token, dictado_id)`: valida token, crea VersionPadron + EntradaPadron en transacción, desactiva versión anterior, registra audit PADRON_CARGAR
  - `obtener_padron_activo(dictado_id)`: devuelve entradas de la versión activa
  - `vaciar_dictado(dictado_id, current_user)`: scope-isolated delete, registra audit PADRON_VACIAR
  - `listar_versiones(dictado_id)`: historial de versiones
- [x] 5.3 Implementar parseo de archivos: soporte .xlsx (openpyxl) y .csv (csv module), validación de columnas requeridas (nombre, apellidos, email, comision, regional)
- [x] 5.4 Escribir tests de servicio: preview (archivo válido, inválido, columnas faltantes), confirm (creación transaccional, desactivación de versión anterior, token expirado, conflict 409), vaciado (scope profesor, scope coordinador, 403 sin permiso, 403 dictado ajeno)

## 6. Integración Moodle WS

- [x] 6.1 Crear `backend/app/integrations/moodle_ws.py` con clase `MoodleClient`:
  - Constructor: recibe config de tenant (base_url, token)
  - Método `sync_usuarios(dictado_id)`: obtiene usuarios inscritos desde Moodle, los mapea a EntradaPadron
  - Método `sync_actividades(dictado_id)`: stub para C-10 (obtiene actividades desde Moodle)
  - Manejo de errores: `MoodleException` con código, mensaje, suggestion de reintento
  - Timeout y retry configurable con `httpx.AsyncClient`
- [x] 6.2 Implementar `MoodleSyncService` en `backend/app/services/padron/moodle_sync_service.py`:
  - `sync_on_demand(dictado_id, current_user)`: invoca MoodleClient, crea padrón vía PadronService
  - `sync_nocturna()`: worker que recorre tenants con Moodle configurado y ejecuta sync por dictado
- [x] 6.3 Escribir tests de MoodleClient: mock de httpx para simular respuestas exitosas, errores 401, timeouts
- [x] 6.4 Escribir tests de MoodleSyncService: sync on-demand exitosa, Moodle caído mapea a 502, sync nocturna falla parcial

## 7. Router y Endpoints

- [x] 7.1 Crear `backend/app/api/v1/routers/padron.py` con:
  - Router prefix `/api/admin/padron`, guard base `PADRON_VER`
  - `POST /preview` (dependencias: `PADRON_IMPORTAR`, UploadFile, Form con dictado_id)
  - `POST /importar` (dependencias: `PADRON_IMPORTAR`, body con token + dictado_id)
  - `GET /dictados/{dictado_id}` (dependencias: `PADRON_VER`)
  - `GET /versiones` (dependencias: `PADRON_VER`, query param dictado_id)
  - `POST /dictados/{dictado_id}/vaciar` (dependencias: `PADRON_VACIAR`)
  - `POST /sync/moodle` (dependencias: `PADRON_IMPORTAR`, body con dictado_id)
- [x] 7.2 Registrar el router en `backend/app/api/v1/__init__.py` o main app
- [x] 7.3 Escribir tests de integración del router: cada endpoint con permisos correctos/incorrectos, payloads válidos/inválidos

## 8. Tests de Integración y Reglas de Negocio

- [x] 8.1 Test: versionado — activar una nueva versión desactiva la anterior
- [x] 8.2 Test: import xlsx/csv — preview muestra resumen, confirm persiste datos
- [x] 8.3 Test: entrada sin usuario_id — alumno sin cuenta se persiste con usuario_id=null
- [x] 8.4 Test: aislamiento tenant — tenant A no ve datos de tenant B
- [x] 8.5 Test: mock Moodle WS — sync exitosa crea padrón; error Moodle → 502
- [x] 8.6 Test: vaciado scope-isolated RN-04 — profesor solo borra sus propios datos; coordinador borra todo
