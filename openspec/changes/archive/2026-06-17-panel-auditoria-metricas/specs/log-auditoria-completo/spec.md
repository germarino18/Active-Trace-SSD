## ADDED Requirements

### Requirement: Log completo de auditoría con filtros

The system SHALL provide a read-only endpoint that returns the full audit log with combined filters: date range (`fecha_desde`, `fecha_hasta`), materia (`materia_id`), user (`usuario_id`), and action code (`accion`). The endpoint SHALL support pagination via `offset` and `limit` (default 50, max 200).

#### Scenario: Log returns paginated results
- **WHEN** a user with `auditoria:ver` calls GET `/api/v1/auditoria/log` with no filters
- **THEN** the response contains the first 50 records sorted by `fecha_hora` descending, plus `total` count and pagination metadata

#### Scenario: Log filters by date range
- **WHEN** a user calls with `fecha_desde=2026-01-01&fecha_hasta=2026-06-30`
- **THEN** only records within that range are returned

#### Scenario: Log filters by materia
- **WHEN** a user calls with `materia_id=uuid`
- **THEN** only records with that materia_id are returned

#### Scenario: Log filters by user
- **WHEN** a user calls with `usuario_id=uuid`
- **THEN** only records with that actor_id are returned

#### Scenario: Log filters by action code
- **WHEN** a user calls with `accion=CALIFICACIONES_IMPORTAR`
- **THEN** only records with that action code are returned

#### Scenario: Log supports combined filters
- **WHEN** a user calls with `usuario_id=uuid&materia_id=uuid&fecha_desde=2026-01-01`
- **THEN** all filters are applied as AND conditions

#### Scenario: Log pagination with offset
- **WHEN** a user calls with `offset=50&limit=25`
- **THEN** records 51-75 are returned

### Requirement: Log returns full record details

Each audit log record returned SHALL include: `id`, `fecha_hora`, `actor_id`, `actor_nombre` (resolved from Usuario), `impersonado_id` (nullable), `materia_id`, `materia_nombre` (nullable, resolved from Materia), `accion`, `detalle` (JSON), `filas_afectadas`, `ip`, `user_agent`.

#### Scenario: Log record includes resolved names
- **WHEN** a record is returned
- **THEN** it includes `actor_nombre` (from Usuario) and optionally `materia_nombre` (from Materia)

### Requirement: Tenant isolation

All log queries SHALL be scoped by `tenant_id` from the authenticated session. A user SHALL never see audit records from another tenant.

#### Scenario: Tenant isolation enforced
- **WHEN** a user from tenant A queries the log
- **THEN** only audit records with tenant A's tenant_id are returned, even if other tenants exist

### Requirement: Read-only endpoint

The log endpoint SHALL only support GET operations. No POST, PUT, PATCH, or DELETE SHALL be exposed on `/api/v1/auditoria/*`.

#### Scenario: Only GET allowed
- **WHEN** a POST request is made to any `/api/v1/auditoria/*` endpoint
- **THEN** the response is 405 Method Not Allowed
