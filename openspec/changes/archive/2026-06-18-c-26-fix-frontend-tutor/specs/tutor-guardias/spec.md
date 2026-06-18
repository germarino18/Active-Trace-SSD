## ADDED Requirements

### Requirement: TUTOR puede registrar una guardia
El sistema DEBE permitir al TUTOR registrar una guardia desde el frontend. Una guardia es un encuentro con `tipo=guardia` que se crea mediante `POST /api/v1/encuentros`.

#### Scenario: TUTOR registra guardia exitosamente
- **WHEN** un TUTOR completa el formulario de guardia (fecha, hora, materia/comisión, observaciones)
- **AND** hace clic en "Registrar Guardia"
- **THEN** el sistema DEBE llamar a `POST /api/v1/encuentros` con `tipo: "guardia"`
- **AND** mostrar un mensaje de éxito "Guardia registrada correctamente"
- **AND** redirigir al listado de guardias

#### Scenario: TUTOR cancela registro de guardia
- **WHEN** un TUTOR abre el formulario de guardia
- **AND** hace clic en "Cancelar"
- **THEN** el formulario DEBE cerrarse sin enviar datos

### Requirement: TUTOR puede ver su historial de guardias
El sistema DEBE mostrar al TUTOR un listado de sus guardias registradas, obtenido del endpoint `GET /api/v1/encuentros?tipo=guardia`.

#### Scenario: TUTOR ve historial de guardias
- **WHEN** un TUTOR navega a `/guardias`
- **THEN** el sistema DEBE mostrar una tabla con fecha, materia, hora, estado de cada guardia
- **AND** DEBE haber un botón "Nueva Guardia" para registrar una nueva
