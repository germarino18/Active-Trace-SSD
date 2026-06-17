## ADDED Requirements

### Requirement: Acciones por día (serie temporal)

The system SHALL provide an endpoint that returns a time-series aggregation of audit actions grouped by day, for a given date range. The response SHALL include the date and the action count per day, sorted chronologically.

#### Scenario: Acciones por día returns daily counts
- **WHEN** a user with `auditoria:ver` calls GET `/api/v1/auditoria/acciones-por-dia` with `fecha_desde` and `fecha_hasta`
- **THEN** the response contains an array of `{fecha: string, total: integer}` sorted by date ascending

#### Scenario: Acciones por día filters by user
- **WHEN** a user with `auditoria:ver` calls the endpoint with `usuario_id` query parameter
- **THEN** only actions performed by that user are included in the aggregation

#### Scenario: Acciones por día filters by materia
- **WHEN** a user with `auditoria:ver` calls the endpoint with `materia_id` query parameter
- **THEN** only actions scoped to that materia are included

### Requirement: Estado de comunicaciones por docente

The system SHALL provide an endpoint that returns the distribution of communication states (Pendiente, Enviando, Enviado, Fallido, Cancelado) aggregated by docente and materia, for a given date range.

#### Scenario: Estado de comunicaciones returns grouped counts
- **WHEN** a user with `auditoria:ver` calls GET `/api/v1/auditoria/comunicaciones-por-docente` with `fecha_desde` and `fecha_hasta`
- **THEN** the response contains an array grouped by `docente_id` and `materia_id`, each with counts per state

#### Scenario: Estado de comunicaciones respects tenant isolation
- **WHEN** a user calls the endpoint
- **THEN** only communications within the user's own tenant are returned

### Requirement: Interacciones por docente y materia

The system SHALL provide an endpoint that returns detailed usage metrics by docente and materia, broken down by action type (e.g., analysis, preview, import, send, cleanup, threshold config, emails generated, batches processed).

#### Scenario: Interacciones returns metrics grouped by docente and materia
- **WHEN** a user with `auditoria:ver` calls GET `/api/v1/auditoria/interacciones-por-docente-materia` with optional `fecha_desde` and `fecha_hasta`
- **THEN** the response contains an array with `docente_id`, `materia_id`, and a breakdown of counts per action code

### Requirement: Últimas acciones (log detallado)

The system SHALL provide an endpoint that returns the most recent audit log entries, with configurable `limit` (default 200, maximum 1000). The response SHALL include each record's full details: fecha_hora, actor_id, materia_id, accion, detalle (JSON), filas_afectadas, ip, user_agent.

#### Scenario: Últimas acciones returns up to N records
- **WHEN** a user with `auditoria:ver` calls GET `/api/v1/auditoria/ultimas-acciones`
- **THEN** the response contains at most 200 records sorted by `fecha_hora` descending

#### Scenario: Últimas acciones respects custom limit
- **WHEN** a user calls with `?limit=50`
- **THEN** the response contains at most 50 records

#### Scenario: Últimas acciones caps limit at 1000
- **WHEN** a user calls with `?limit=5000`
- **THEN** the response contains at most 1000 records (cap applied)

#### Scenario: Últimas acciones filters by date range
- **WHEN** a user calls with `fecha_desde` and `fecha_hasta`
- **THEN** only records within that date range are returned

#### Scenario: Últimas acciones filters by materia
- **WHEN** a user calls with `materia_id`
- **THEN** only records with that materia_id are included

#### Scenario: Últimas acciones filters by user
- **WHEN** a user calls with `usuario_id`
- **THEN** only records with that actor_id are included

### Requirement: Scope (propio) for COORDINADOR

The system SHALL enforce scope `(propio)` for COORDINADOR on all audit panel endpoints. A COORDINADOR with `auditoria:ver` SHALL only see audit records whose `actor_id` matches users under their supervision (resolved via `Asignacion`). ADMIN and FINANZAS SHALL see all records within their tenant.

#### Scenario: COORDINADOR sees only supervised users
- **WHEN** a COORDINADOR with `auditoria:ver` calls any audit panel endpoint
- **THEN** the results are filtered to only include records from users assigned to materias/carreras where the COORDINADOR supervises

#### Scenario: ADMIN sees all records in tenant
- **WHEN** an ADMIN with `auditoria:ver` calls any audit panel endpoint
- **THEN** all records within the ADMIN's tenant are returned without scope filtering
