## ADDED Requirements

### Requirement: Reserva de turno por ALUMNO
El sistema SHALL permitir que un ALUMNO con permiso `coloquios:reservar` reserve un turno en una convocatoria Activa para la cual esté habilitado (importado). La reserva SHALL crear un registro `ReservaEvaluacion` con `evaluacion_id`, `alumno_id`, `fecha_hora` (momento de la reserva), y `estado = Activa`. SHALL verificarse que haya cupo disponible (`reservas_activas < cupo_maximo`). La verificación de cupo SHALL hacerse dentro de una transacción con `SELECT ... FOR UPDATE` para evitar race conditions.

#### Scenario: ALUMNO habilitado reserva con cupo disponible
- **WHEN** un ALUMNO que está importado en una convocatoria Activa con cupo disponible (10 reservas activas, cupo_maximo = 30) solicita reservar
- **THEN** se crea una ReservaEvaluacion con estado Activa, el contador de reservas activas se incrementa, y se registra auditoría con código `COLOQUIO_RESERVAR`

#### Scenario: ALUMNO no habilitado intenta reservar
- **WHEN** un ALUMNO que NO está importado en la convocatoria intenta reservar
- **THEN** el sistema rechaza la operación con error 403

#### Scenario: Sin cupo disponible es rechazado
- **WHEN** un ALUMNO intenta reservar en una convocatoria con cupo agotado (reservas activas >= cupo_maximo)
- **THEN** el sistema rechaza la operación con error 422 y mensaje "Cupo agotado"

#### Scenario: ALUMNO ya reservado no puede reservar otra vez
- **WHEN** un ALUMNO que ya tiene una reserva Activa en la misma convocatoria intenta reservar nuevamente
- **THEN** el sistema rechaza la operación con error 422 (ya tiene reserva activa)

#### Scenario: Reserva en convocatoria Cerrada es rechazada
- **WHEN** un ALUMNO intenta reservar en una convocatoria en estado Cerrada
- **THEN** el sistema rechaza la operación con error 422

#### Scenario: Race condition en último cupo
- **WHEN** dos ALUMNOS intentan reservar el último cupo simultáneamente
- **THEN** exactamente una reserva se crea exitosamente y la otra es rechazada con error de cupo agotado (la transacción con FOR UPDATE garantiza consistencia)

#### Scenario: Aislamiento multi-tenant en reserva
- **WHEN** un ALUMNO del Tenant A intenta reservar en una convocatoria del Tenant B
- **THEN** el sistema rechaza la operación (la convocatoria no es visible para el alumno)

### Requirement: Cancelación de reserva por ALUMNO
El sistema SHALL permitir que un ALUMNO cancele su propia reserva Activa. Una reserva Cancelada NO puede reactivarse. La cancelación SHALL liberar el cupo para otro ALUMNO. Sólo el ALUMNO titular de la reserva o un usuario con `coloquios:gestionar` PUEDE cancelarla.

#### Scenario: ALUMNO cancela su propia reserva
- **WHEN** un ALUMNO cancela su reserva Activa en una convocatoria Activa
- **THEN** la reserva pasa a estado Cancelada, el cupo se libera, y se registra auditoría con código `COLOQUIO_CANCELAR_RESERVA`

#### Scenario: ALUMNO cancela reserva de otro ALUMNO es rechazado
- **WHEN** un ALUMNO intenta cancelar la reserva de otro ALUMNO
- **THEN** el sistema rechaza la operación con error 403

#### Scenario: COORDINADOR cancela reserva de cualquier ALUMNO
- **WHEN** un COORDINADOR con permiso `coloquios:gestionar` cancela la reserva Activa de un ALUMNO
- **THEN** la reserva pasa a estado Cancelada y el cupo se libera

#### Scenario: Cancelar reserva ya cancelada es idempotente
- **WHEN** un ALUMNO intenta cancelar una reserva ya en estado Cancelada
- **THEN** el sistema responde exitosamente (200, sin cambios)

#### Scenario: Cancelar reserva en convocatoria Cerrada es rechazado
- **WHEN** un ALUMNO intenta cancelar su reserva en una convocatoria Cerrada
- **THEN** el sistema rechaza la operación con error 422

### Requirement: Agenda consolidada de reservas activas
El sistema SHALL exponer un endpoint con permiso `coloquios:ver` que liste todas las reservas activas del tenant. SHALL soportar filtros opcionales: `evaluacion_id`, `alumno_id`, `dictado_id`, `fecha_desde`, `fecha_hasta`. Para COORDINADOR/ADMIN: global. Para PROFESOR: solo reservas de sus dictados `(propio)`.

#### Scenario: COORDINADOR consulta agenda global
- **WHEN** un COORDINADOR consulta la agenda de reservas activas sin filtros
- **THEN** el sistema devuelve todas las reservas Activas del tenant, ordenadas por fecha_hora descendente

#### Scenario: PROFESOR consulta agenda de sus dictados
- **WHEN** un PROFESOR consulta la agenda
- **THEN** el sistema devuelve solo las reservas de convocatorias cuyos dictados le pertenecen (tiene asignación vigente)

#### Scenario: Filtrar agenda por dictado y fecha
- **WHEN** un COORDINADOR consulta la agenda con filtros `dictado_id = X` y `fecha_desde = "2026-06-01"`
- **THEN** el sistema devuelve solo las reservas que cumplen ambos filtros
