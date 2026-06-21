## ADDED Requirements

### Requirement: PROFESOR can send a communication to overdue students without selecting an activity
The system SHALL allow a PROFESOR to enqueue a communication to overdue students with the activity reference being OPTIONAL. When `actividad_id` is omitted (null), the communication MUST still be enqueued and MUST NOT be tied to any activity.

#### Scenario: Send communication omitting the activity
- **WHEN** the PROFESOR calls `POST /api/v1/profesor/comunicado-atrasados-flexible` with `actividad_id` set to null and a non-empty `destinatarios` list
- **THEN** the system enqueues the communication for each resolved destinatario
- **THEN** the system does NOT require an activity and renders the templates using only `{alumno_nombre, alumno_apellido, materia, docente_nombre}`
- **THEN** the audit entry records `actividad_id: null`

#### Scenario: Activity provided is validated
- **WHEN** the PROFESOR provides a non-null `actividad_id`
- **THEN** the system validates the activity belongs to the tenant and to the destinatario's dictado
- **THEN** if the activity does not exist or is not in the tenant, the system responds 404 and enqueues nothing

### Requirement: PROFESOR can send a communication to a single overdue student (individual mode)
The system SHALL accept a `destinatarios` list of exactly one element and enqueue the communication only for that student.

#### Scenario: Individual send
- **WHEN** the PROFESOR submits a request with a single-element `destinatarios` list referencing one `entrada_padron_id` and its `dictado_id`
- **THEN** the system enqueues exactly one communication for that student (if the student has a valid email)
- **THEN** the response `total` is 1

#### Scenario: Single student without email
- **WHEN** the only destinatario has no email on its padron entry
- **THEN** the system enqueues nothing and the response `total` is 0

### Requirement: PROFESOR can send a communication to all overdue students (general mode), across materias
The system SHALL accept a `destinatarios` list spanning multiple dictados and materias and enqueue the same message to all of them, grouping by materia.

#### Scenario: General send across materias
- **WHEN** the PROFESOR submits a `destinatarios` list whose entries belong to two or more different materias
- **THEN** the system groups destinatarios by materia and calls the bulk-enqueue pipeline once per materia
- **THEN** the response `total` equals the number of students with a valid email across all materias
- **THEN** the response includes the list of generated `lotes`

### Requirement: The flexible communication endpoint reuses the approval-gated pipeline
The system SHALL route every flexible communication through the existing approval-gated bulk pipeline (`enqueue_masivo`) and SHALL NOT transition communication states directly nor bypass tenant approval.

#### Scenario: Tenant requires approval
- **WHEN** the tenant has `aprobacion_comunicaciones = true`
- **THEN** the enqueued communications remain pending for human approval (Pend) and are NOT auto-sent
- **THEN** they only transition to Enviando through the existing approval action

#### Scenario: Tenant does not require approval
- **WHEN** the tenant has `aprobacion_comunicaciones = false`
- **THEN** the enqueued communications transition to Enviando automatically, consistent with the existing bulk pipeline

### Requirement: The flexible communication endpoint enforces RBAC, tenant scoping and audit
The system SHALL gate the endpoint with `Perm.COMUNICACION_ENVIAR` (fail-closed), resolve the actor identity from the verified session (JWT), scope every lookup by `tenant_id`, and record an audit entry.

#### Scenario: Missing permission is rejected
- **WHEN** a user without `COMUNICACION_ENVIAR` calls the endpoint
- **THEN** the system responds 403 and enqueues nothing

#### Scenario: Destinatarios are validated against tenant and the professor's dictados
- **WHEN** a `destinatario` references an `entrada_padron_id` or `dictado_id` outside the actor's tenant or not among the professor's vigente dictados
- **THEN** that destinatario is rejected/discarded and is not enqueued

#### Scenario: Request rejects unknown fields
- **WHEN** the request body contains a field not declared in the schema
- **THEN** the system responds 422 (Pydantic `extra='forbid'`)

#### Scenario: Audit is recorded
- **WHEN** a flexible communication is enqueued
- **THEN** the system records an audit entry for the send, including the resolved total and `actividad_id` (or null)
