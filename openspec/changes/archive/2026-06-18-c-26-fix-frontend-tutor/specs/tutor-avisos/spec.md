## ADDED Requirements

### Requirement: TUTOR puede confirmar avisos (acknowledgment)
El sistema DEBE permitir al TUTOR confirmar la recepción de avisos mediante el endpoint `POST /api/v1/avisos/:id/ack`.

#### Scenario: TUTOR confirma aviso exitosamente
- **WHEN** un TUTOR ve un aviso pendiente en la tabla de avisos
- **AND** hace clic en "Confirmar"
- **THEN** el sistema DEBE llamar a `POST /api/v1/avisos/:id/ack`
- **AND** mostrar un mensaje de éxito "Aviso confirmado"
- **AND** deshabilitar el botón de confirmación para ese aviso

#### Scenario: TUTOR intenta confirmar aviso ya confirmado
- **WHEN** un TUTOR hace clic en "Confirmar" en un aviso ya acked
- **THEN** el sistema DEBE mostrar un mensaje de error o ignorar la acción
- **AND** el botón DEBE estar deshabilitado

### Requirement: TUTOR ve avisos pendientes en tabla
El sistema DEBE mostrar los avisos del TUTOR con una columna de acción "Confirmar" para avisos no leídos.

#### Scenario: TUTOR ve tabla de avisos
- **WHEN** un TUTOR navega a `/avisos`
- **THEN** el sistema DEBE mostrar una tabla con: título, fecha, mensaje, estado
- **AND** para avisos no confirmados, DEBE mostrar un botón "Confirmar"
- **AND** para avisos confirmados, DEBE mostrar un badge "Confirmado"
