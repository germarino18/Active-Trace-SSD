## ADDED Requirements

### Requirement: Append-only audit log model
The system SHALL persist every significant action in an `AuditLog` record that is immutable. The record MUST capture, at minimum: `tenant_id`, `fecha_hora`, `actor_id` (the real actor), `impersonado_id` (nullable), `materia_id` (nullable), `accion` (standardized code), `detalle` (JSON), `filas_afectadas` (integer), `ip`, and `user_agent`. No application code path SHALL update or delete an audit record.

#### Scenario: Audit record is created with full attribution
- **WHEN** a significant action is logged for an authenticated actor
- **THEN** a new `audit_log` row is persisted with the actor's `tenant_id`, the action code, the affected-row count, and the request IP and user-agent

#### Scenario: Repository exposes no mutation methods
- **WHEN** the `AuditLogRepository` API is inspected
- **THEN** it exposes only create and read/list operations and offers no `update` or `delete` method

### Requirement: Database-level append-only enforcement
The system SHALL reject `UPDATE` and `DELETE` against the `audit_log` table at the PostgreSQL level, independent of the application layer, so that a direct SQL statement cannot tamper with the trail.

#### Scenario: Direct UPDATE is rejected
- **WHEN** a raw SQL `UPDATE audit_log SET ...` is executed against an existing row
- **THEN** the database raises an error and no row is modified

#### Scenario: Direct DELETE is rejected
- **WHEN** a raw SQL `DELETE FROM audit_log WHERE ...` is executed
- **THEN** the database raises an error and no row is removed

### Requirement: Tenant isolation of the audit trail
The audit log SHALL be scoped by `tenant_id`; reads and lists MUST be filtered by the authenticated user's tenant by default, and a write MUST stamp the actor's tenant.

#### Scenario: Reads are tenant-scoped
- **WHEN** a user lists audit records
- **THEN** only records whose `tenant_id` matches the user's tenant are returned

### Requirement: Standardized action codes
The system SHALL identify each audited action by a standardized textual code defined as a type-safe constant. The catalog MUST include `IMPERSONACION_INICIAR` and `IMPERSONACION_FINALIZAR`, and SHALL forward-declare the codes used by future capabilities (`CALIFICACIONES_IMPORTAR`, `PADRON_CARGAR`, `PADRON_VACIAR`, `COMUNICACION_ENVIAR`, `ASIGNACION_MODIFICAR`, `LIQUIDACION_CERRAR`, `UMBRAL_CONFIGURAR`).

#### Scenario: Action codes are referenced by constant
- **WHEN** an action is logged
- **THEN** the `accion` field stores the value of a defined constant rather than an inline string literal

#### Scenario: PADRON_VACIAR is declared and usable
- **WHEN** the system logs a vaciado operation
- **THEN** the `accion` field uses the `PADRON_VACIAR` constant

#### Scenario: UMBRAL_CONFIGURAR is declared and usable
- **WHEN** the system logs an umbral configuration operation
- **THEN** the `accion` field uses the `UMBRAL_CONFIGURAR` constant

### Requirement: Reusable audit logging helper
The system SHALL provide a reusable helper that any service or endpoint can call to write an audit record. The helper MUST derive `actor_id` and `impersonado_id` from the verified session such that the actor is ALWAYS the real authenticated user, never the impersonated one.

#### Scenario: Attribution under a normal session
- **WHEN** an action is logged for a non-impersonated session
- **THEN** `actor_id` is the session user and `impersonado_id` is null

#### Scenario: Attribution under an impersonation session
- **WHEN** an action is logged while an impersonation session is active
- **THEN** `actor_id` is the real actor (the impersonator) and `impersonado_id` is the impersonated user
