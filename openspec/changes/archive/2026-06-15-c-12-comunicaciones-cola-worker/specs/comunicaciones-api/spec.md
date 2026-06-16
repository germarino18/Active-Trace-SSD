## ADDED Requirements

### Requirement: Preview de comunicación antes de encolar
El sistema SHALL permitir generar una vista previa del mensaje (asunto + cuerpo) antes de encolar una comunicación, aplicando las plantillas con variables de sustitución contra los datos del destinatario.

#### Scenario: Preview exitosa
- **WHEN** un usuario con permiso `comunicacion:enviar` solicita preview con un destinatario_id, asunto con variables y cuerpo con variables
- **THEN** el sistema retorna el asunto y cuerpo con las variables sustituidas por los datos reales del destinatario

#### Scenario: Preview sin variables
- **WHEN** un usuario solicita preview con un asunto y cuerpo sin variables de sustitución
- **THEN** el sistema retorna el asunto y cuerpo sin modificar

#### Scenario: Preview con destinatario inexistente
- **WHEN** un usuario solicita preview con un destinatario_id que no existe en el tenant
- **THEN** el sistema retorna 404

### Requirement: Envío masivo de comunicaciones con cola
El sistema SHALL permitir encolar un envío masivo de comunicaciones para múltiples destinatarios, creando un registro `Comunicacion` por cada destinatario en estado Pendiente, agrupados por un mismo `lote_id`.

#### Scenario: Envío masivo exitoso
- **WHEN** un usuario con permiso `comunicacion:enviar` envía una lista de 3 o más destinatarios con el mismo asunto y cuerpo
- **THEN** el sistema crea N registros `Comunicacion`, todos con el mismo `lote_id`, cada uno en estado Pendiente

#### Scenario: Envío masivo sin destinatarios
- **WHEN** un usuario intenta encolar un envío masivo con lista de destinatarios vacía
- **THEN** el sistema retorna 422 (error de validación)

### Requirement: Tracking de estado de comunicaciones
El sistema SHALL exponer el estado actual de cada comunicación y permitir consultar el estado de un lote completo.

#### Scenario: Consultar estado de una comunicación individual
- **WHEN** un usuario con permiso `comunicacion:enviar` consulta una comunicación por ID
- **THEN** el sistema retorna el registro incluyendo estado, lote_id, asunto, y enviado_at (si aplica)

#### Scenario: Consultar estado de un lote completo
- **WHEN** un usuario consulta un lote por lote_id
- **THEN** el sistema retorna todos los registros del lote con un resumen: total, Pendientes, Enviados, Errores, Cancelados

#### Scenario: Usuario sin permiso no puede ver comunicaciones de otro docente
- **WHEN** un usuario sin permiso `comunicacion:enviar` consulta comunicaciones
- **THEN** el sistema retorna 403

### Requirement: Aprobación de envíos masivos (configurable por tenant)
El sistema SHALL permitir que, si el tenant tiene habilitada la aprobación de comunicaciones, los envíos masivos queden en estado Pendiente hasta que un usuario con permiso `comunicacion:aprobar` los apruebe (transición a Enviando) o los cancele.

#### Scenario: Aprobación de lote completo
- **WHEN** un usuario con permiso `comunicacion:aprobar` aprueba un lote_id completo
- **THEN** todas las comunicaciones Pendiente de ese lote pasan a Enviando

#### Scenario: Aprobación individual dentro de un lote
- **WHEN** un usuario con permiso `comunicacion:aprobar` aprueba una comunicación individual
- **THEN** esa comunicación pasa de Pendiente a Enviando

#### Scenario: Cancelación de comunicación
- **WHEN** un usuario con permiso `comunicacion:aprobar` cancela una comunicación en estado Pendiente
- **THEN** la comunicación pasa a estado Cancelado

#### Scenario: Cancelación de lote completo
- **WHEN** un usuario con permiso `comunicacion:aprobar` cancela un lote_id completo
- **THEN** todas las comunicaciones Pendiente de ese lote pasan a Cancelado

#### Scenario: Transición inválida desde Enviado
- **WHEN** un usuario intenta cancelar una comunicación en estado Enviado
- **THEN** el sistema rechaza la operación con error 409 (conflicto de estado)

#### Scenario: Transición inválida desde Error
- **WHEN** un usuario intenta aprobar una comunicación en estado Error
- **THEN** el sistema rechaza la operación con error 409

#### Scenario: Tenant sin aprobación no bloquea envío
- **WHEN** el tenant tiene aprobación desactivada y un usuario envía un lote masivo
- **THEN** las comunicaciones pasan directamente a Enviando (no quedan retenidas)

#### Scenario: Usuario sin permiso no puede aprobar
- **WHEN** un usuario sin permiso `comunicacion:aprobar` intenta aprobar un lote
- **THEN** el sistema retorna 403

### Requirement: Auditoría de envíos
El sistema SHALL registrar un evento de auditoría con código `COMUNICACION_ENVIAR` cada vez que se encola un envío masivo, incluyendo cantidad de destinatarios y lote_id.

#### Scenario: Auditoría al encolar envío masivo
- **WHEN** un usuario confirma un envío masivo
- **THEN** se crea un registro AuditLog con accion="COMUNICACION_ENVIAR", detalle={cantidad, lote_id}
