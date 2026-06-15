## Why

Activia-Trace necesita un módulo de **Padrón** que permita gestionar el listado de alumnos inscriptos por dictado (materia × cohorte), con soporte para importación desde Moodle Web Services, fallback manual via `.xlsx`/`.csv`, versionado de padrones (solo una versión activa por dictado) y la operación de vaciado de datos de una materia (scope por `usuario_id × materia_id`). Sin este módulo no es posible asociar alumnos a cursadas, importar calificaciones ni ejecutar los flujos de comunicación y trazabilidad.

## What Changes

- **Nuevos modelos**: `VersionPadron` y `EntradaPadron` con versionado (una activa por dictado_id; activar una nueva desactiva la anterior)
- **Migración Alembic** 008: creación de tablas `version_padron` y `entrada_padron`
- **Nuevos permisos RBAC**: `padron:importar`, `padron:vaciar`, `padron:ver`
- **Endpoint Importar padrón** (`POST /api/admin/padron/importar`): acepta archivo `.xlsx`/`.csv` con preview previa, upsert destructivo (crea nueva versión activa, desactiva la anterior). Gated por `padron:importar`.
- **Endpoint Preview importación** (`POST /api/admin/padron/preview`): previsualiza filas sin persistir
- **Endpoint Vaciar datos de materia** (`POST /api/admin/padron/dictados/{dictado_id}/vaciar`): elimina los datos de padrón y calificaciones del usuario actual para esa materia (RN-04). Gated por `padron:vaciar`.
- **Integración Moodle WS**: cliente dedicado en `integrations/moodle_ws.py` para sync de usuarios/actividades, nocturna automática + on-demand; errores mapean a `502` con reintento.
- **Auditoría**: code `PADRON_CARGAR` (ya declarado en audit-log spec) y `PADRON_VACIAR`
- **Route prefix**: `/api/admin/padron` bajo guard RBAC

## Capabilities

### New Capabilities
- `padron-versionado`: creación, activación y desactivación de versiones de padrón por dictado_id, con la regla de que solo una versión puede estar activa simultáneamente
- `padron-ingesta-archivos`: importación de padrón desde `.xlsx`/`.csv` con preview en dos pasos, upsert destructivo (reemplaza versión activa anterior), validación de columnas y cifrado AES-256 de email
- `padron-integracion-moodle`: sincronización de usuarios/actividades via Moodle Web Services API, sync nocturna + on-demand, fallback manual a archivos cuando el tenant no tiene WS configurado, errores mapean a `502` con reintento
- `padron-vaciado`: eliminación scope-isolated de datos de padrín y calificaciones para un `(usuario_id × dictado_id)`, registrado en audit log

### Modified Capabilities
- `audit-log`: forward-declare `PADRON_CARGAR` y `PADRON_VACIAR` como códigos de acción estandarizados (ya declarado `PADRON_CARGAR` en spec existente, confirmar que `PADRON_VACIAR` también se agregue)

## Impact

- **Backend models**: nuevos archivos `backend/app/models/version_padron.py` y `backend/app/models/entrada_padron.py`
- **Backend router**: nuevo archivo `backend/app/api/v1/routers/padron.py`
- **Backend services**: nuevo directorio `backend/app/services/padron/` con `padron_service.py` y `moodle_sync_service.py`
- **Backend repositories**: nuevos `version_padron_repository.py` y `entrada_padron_repository.py`
- **Backend schemas**: nuevos Pydantic DTOs en `backend/app/schemas/padron.py`
- **Integration**: implementación de `backend/app/integrations/moodle_ws.py`
- **Permissions**: nuevos códigos en `backend/app/core/permissions.py`: `PADRON_IMPORTAR`, `PADRON_VACIAR`, `PADRON_VER`
- **Alembic migration**: nueva migración 008
- **Audit log**: nuevos action codes en la constante de acciones
- **Config**: clave `ENCRYPTION_KEY` para cifrado de email en EntradaPadron
- **Tests**: nuevo directorio `backend/tests/padron/`
