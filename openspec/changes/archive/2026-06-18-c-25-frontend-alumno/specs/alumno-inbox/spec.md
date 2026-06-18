## ADDED Requirements

### Requirement: Bandeja de mensajes internos del alumno
El sistema SHALL mostrar al alumno los hilos de mensajes internos (inbox).

#### Scenario: Inbox muestra hilos recibidos
- **WHEN** el alumno autenticado accede a `/alumno/inbox`
- **THEN** el sistema MUST mostrar los hilos de mensaje donde el alumno es destinatario
- **AND** cada hilo MUST incluir: remitente, asunto, último mensaje (fragmento), fecha, indicador de no leído

#### Scenario: Inbox vacío
- **WHEN** el alumno no tiene mensajes
- **THEN** el sistema MUST mostrar "No tenés mensajes"

### Requirement: Lectura y respuesta en hilo
El sistema SHALL permitir al alumno leer un hilo y responder dentro del mismo.

#### Scenario: Lectura del hilo
- **WHEN** el alumno hace clic en un hilo
- **THEN** el sistema MUST mostrar todos los mensajes del hilo en orden cronológico
- **AND** el sistema MUST marcar el hilo como leído

#### Scenario: Respuesta en el hilo
- **WHEN** el alumno escribe y envía una respuesta dentro del hilo
- **THEN** el sistema MUST agregar el mensaje al hilo
- **AND** el sistema MUST mostrar el nuevo mensaje inmediatamente en la conversación
