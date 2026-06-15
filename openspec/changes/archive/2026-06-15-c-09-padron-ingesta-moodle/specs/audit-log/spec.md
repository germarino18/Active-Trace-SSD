## MODIFIED Requirements

### Requirement: Standardized action codes

The system SHALL identify each audited action by a standardized textual code defined as a type-safe constant. The catalog MUST include `IMPERSONACION_INICIAR` and `IMPERSONACION_FINALIZAR`, and SHALL forward-declare the codes used by future capabilities (`CALIFICACIONES_IMPORTAR`, `PADRON_CARGAR`, `PADRON_VACIAR`, `COMUNICACION_ENVIAR`, `ASIGNACION_MODIFICAR`, `LIQUIDACION_CERRAR`).

#### Scenario: Action codes are referenced by constant
- **WHEN** an action is logged
- **THEN** the `accion` field stores the value of a defined constant rather than an inline string literal

#### Scenario: PADRON_VACIAR is declared and usable
- **WHEN** the system logs a vaciado operation
- **THEN** the `accion` field uses the `PADRON_VACIAR` constant
