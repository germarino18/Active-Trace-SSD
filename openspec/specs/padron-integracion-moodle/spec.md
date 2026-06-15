## ADDED Requirements

### Requirement: Moodle Web Services client implementation

El sistema SHALL proveer un cliente dedicado en `integrations/moodle_ws.py` que se comunique con la API de Moodle Web Services para sincronizar usuarios y actividades. El cliente SHALL ser configurable por tenant (URL base + token, almacenados cifrados). SHALL usar `httpx.AsyncClient` con timeout configurable. Errores de conexión, autenticación o timeout SHALL mapear a una excepción interna que el endpoint traduce a HTTP 502 con metadatos de reintento.

#### Scenario: Sync de usuarios desde Moodle
- **WHEN** se invoca `sync_usuarios(dictado_id)` y Moodle responde exitosamente
- **THEN** los usuarios obtenidos se importan como nuevo padrón para ese dictado (mismo flujo de versionado)
- **THEN** se registra `PADRON_CARGAR` en audit log con origen "moodle"

#### Scenario: Moodle WS devuelve error
- **WHEN** Moodle responde con error de autenticación o timeout
- **THEN** el cliente lanza `MoodleException` y el endpoint responde 502 Bad Gateway con detalle del error y sugerencia de reintento

#### Scenario: Moodle WS no configurado para el tenant
- **WHEN** se intenta sync para un tenant sin configuración de Moodle WS
- **THEN** el endpoint responde con un error indicando que la integración no está configurada

### Requirement: Sync nocturna automática

El sistema SHALL ejecutar una sync nocturna automática de padrón para todos los dictados activos de tenants que tengan Moodle WS configurado. La sync SHALL dispararse desde el worker background (cola de comunicaciones). SHALL registrar éxito/fallo por dictado en audit log.

#### Scenario: Sync nocturna exitosa
- **WHEN** el worker ejecuta la sync nocturna para un tenant con Moodle configurado
- **THEN** para cada dictado activo se ejecuta `sync_usuarios` y se registra el resultado en audit log

#### Scenario: Sync nocturna falla para un dictado
- **WHEN** la sync nocturna falla para un dictado específico (Moodle caído)
- **THEN** el worker registra el fallo en audit log y continúa con el siguiente dictado (no aborta toda la tanda)

### Requirement: Sync on-demand

El sistema SHALL exponer un endpoint `POST /api/admin/padron/sync/moodle` que dispare una sync inmediata para un dictado específico, gated por `padron:importar`.

#### Scenario: Sync on-demand exitosa
- **WHEN** un usuario autorizado invoca sync on-demand para un dictado
- **THEN** el sistema ejecuta la sincronización y devuelve el resultado (versión creada o error)
