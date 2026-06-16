## ADDED Requirements

### Requirement: Worker consume cola de comunicaciones Pendiente
El worker SHALL ejecutar un loop asíncrono que periódicamente consulta comunicaciones en estado Pendiente y las procesa.

#### Scenario: Worker procesa comunicaciones Pendiente
- **WHEN** el worker ejecuta su ciclo de polling y encuentra comunicaciones Pendiente
- **THEN** las transiciona a Enviando, intenta el envío, y las marca como Enviado o Error según el resultado

#### Scenario: Worker no procesa comunicaciones en otros estados
- **WHEN** el worker ejecuta su ciclo y solo encuentra comunicaciones en estados Enviado, Error o Cancelado
- **THEN** el worker no realiza ninguna acción

### Requirement: Timeout y reintentos en worker
El sistema SHALL manejar timeouts en el worker: si una comunicación permanece en estado Enviando por más de 5 minutos sin completarse, se reintenta (máximo 3 intentos) y luego pasa a Error.

#### Scenario: Reintento por timeout
- **WHEN** una comunicación está en Enviando por más de 5 minutos
- **THEN** el worker la reintenta hasta 3 veces, y si persiste el error, pasa a Error

#### Scenario: Registro de intentos fallidos
- **WHEN** una comunicación falla en el worker
- **THEN** el sistema registra un contador de reintentos (no visible en el modelo actual, pero trazable en logs)

### Requirement: Plantillas con variables de sustitución
El sistema SHALL soportar plantillas con las variables `$alumno_nombre`, `$alumno_apellido`, `$materia`, `$docente_nombre` en asunto y cuerpo.

#### Scenario: Sustitución de todas las variables
- **WHEN** se renderiza una plantilla con `$alumno_nombre`, `$alumno_apellido`, `$materia` y `$docente_nombre`
- **THEN** cada variable se reemplaza por el valor correspondiente del destinatario y contexto

#### Scenario: Variable no encontrada en template
- **WHEN** se renderiza una plantilla con una variable no soportada (ej: `$inexistente`)
- **THEN** el sistema lanza error de validación indicando la variable no reconocida

### Requirement: Logs estructurados del worker
El worker SHALL emitir logs estructurados en JSON con trace_id, lote_id, comunicación_id y resultado del envío.

#### Scenario: Worker loguea procesamiento exitoso
- **WHEN** el worker procesa una comunicación exitosamente
- **THEN** emite un log con level=INFO, lote_id, comunicacion_id, resultado="Enviado"

#### Scenario: Worker loguea error de procesamiento
- **WHEN** el worker falla al procesar una comunicación
- **THEN** emite un log con level=ERROR, lote_id, comunicacion_id, resultado="Error", detalle del error
