## ADDED Requirements

### Requirement: Listado de convocatorias abiertas
El sistema SHALL mostrar al alumno las convocatorias a coloquio en las que puede reservar turno.

#### Scenario: Listado muestra convocatorias disponibles
- **WHEN** el alumno autenticado accede a `/alumno/coloquios`
- **THEN** el sistema MUST mostrar las convocatorias activas de las materias que cursa
- **AND** cada convocatoria MUST incluir: materia, fechas disponibles, cupos restantes, fecha límite de reserva

#### Scenario: Sin convocatorias muestra empty state
- **WHEN** no hay convocatorias activas para las materias del alumno
- **THEN** el sistema MUST mostrar "No hay coloquios disponibles en este momento"

### Requirement: Reserva de turno
El sistema SHALL permitir al alumno reservar un turno en una convocatoria abierta.

#### Scenario: Reserva exitosa
- **WHEN** el alumno selecciona una fecha con cupo disponible y confirma la reserva
- **THEN** el sistema MUST decrementar el cupo y mostrar confirmación visual
- **AND** el sistema MUST persistir la reserva en estado Activa

#### Scenario: Reserva sin cupo rechazada
- **WHEN** el alumno intenta reservar en una fecha sin cupo
- **THEN** el sistema MUST mostrar error "No hay cupos disponibles para esta fecha"
- **AND** el sistema MUST NO crear la reserva

#### Scenario: Reserva duplicada rechazada
- **WHEN** el alumno ya tiene una reserva activa en la misma convocatoria
- **THEN** el sistema MUST mostrar error "Ya tenés una reserva activa en esta convocatoria"

### Requirement: Cancelación de reserva propia
El sistema SHALL permitir al alumno cancelar su propia reserva.

#### Scenario: Cancelación exitosa
- **WHEN** el alumno cancela su reserva activa
- **THEN** el sistema MUST cambiar la reserva a estado Cancelada
- **AND** el sistema MUST incrementar el cupo de la fecha correspondiente
