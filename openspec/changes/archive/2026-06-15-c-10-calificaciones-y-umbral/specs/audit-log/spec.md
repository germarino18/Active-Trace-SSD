## MODIFIED Requirements

### Requirement: Standardized action codes

The system SHALL identify each audited action by a standardized textual code defined as a type-safe constant. The catalog MUST include `IMPERSONACION_INICIAR` and `IMPERSONACION_FINALIZAR`, and SHALL forward-declare the codes used by future capabilities (`CALIFICACIONES_IMPORTAR`, `PADRON_CARGAR`, `PADRON_VACIAR`, `COMUNICACION_ENVIAR`, `ASIGNACION_MODIFICAR`, `LIQUIDACION_CERRAR`).

*Note: `CALIFICACIONES_IMPORTAR` was already forward-declared in the original spec and the constant exists in `AccionAuditoria`. No code change required. The new `UMBRAL_CONFIGURAR` action code SHALL be added.*

#### Scenario: UMBRAL_CONFIGURAR is declared and usable
- **WHEN** the system logs an umbral configuration operation
- **THEN** the `accion` field uses the `UMBRAL_CONFIGURAR` constant
