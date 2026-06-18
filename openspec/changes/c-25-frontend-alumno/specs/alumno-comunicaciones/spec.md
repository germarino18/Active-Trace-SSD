## ADDED Requirements

### Requirement: Historial de comunicaciones recibidas
El sistema SHALL mostrar al alumno el historial de comunicaciones que le fueron enviadas a través del sistema de cola (C-12).

#### Scenario: Listado de comunicaciones recibidas
- **WHEN** el alumno autenticado accede a `/alumno/comunicaciones`
- **THEN** el sistema MUST mostrar las comunicaciones cuyo destinatario sea el alumno
- **AND** cada comunicación MUST incluir: remitente (docente), materia, asunto, fecha de envío, estado (Enviado/Error)

#### Scenario: Comunicación sin destinatario alumno no aparece
- **WHEN** la comunicación fue enviada a otros alumnos pero no a este
- **THEN** el sistema MUST NO incluirla en el listado

#### Scenario: Sin comunicaciones muestra empty state
- **WHEN** el alumno no tiene comunicaciones recibidas
- **THEN** el sistema MUST mostrar "No recibiste comunicaciones"

### Requirement: Vista detalle de comunicación
El sistema SHALL mostrar el contenido completo de una comunicación recibida.

#### Scenario: Vista detalle muestra contenido
- **WHEN** el alumno hace clic en una comunicación del listado
- **THEN** el sistema MUST mostrar: asunto, cuerpo completo del mensaje, remitente, materia, fecha de envío, estado de entrega
