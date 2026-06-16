## ADDED Requirements

### Requirement: User can confirm an aviso that requires acknowledgment
The system SHALL allow any authenticated user to confirm an aviso where `requiere_ack=true` by creating an AcknowledgmentAviso record. The endpoint is available to any role (all have `avisos:confirmar`).

#### Scenario: Confirm aviso successfully
- **WHEN** an ALUMNO sends POST /api/v1/avisos/{id}/confirmar
- **AND** the aviso exists, is active, is within visibility window, and requires_ack=true
- **THEN** the system creates an AcknowledgmentAviso record and returns 200 with { "status": "confirmed" }

#### Scenario: Confirm aviso that does not require ack
- **WHEN** a user sends POST /api/v1/avisos/{id}/confirmar
- **AND** the aviso has requiere_ack=false
- **THEN** the system returns 200 with { "status": "not_required" }

#### Scenario: Duplicate confirmation is idempotent
- **WHEN** a user sends POST /api/v1/avisos/{id}/confirmar twice
- **THEN** the second request returns 200 with { "status": "already_confirmed" } (no duplicate row created)

#### Scenario: Confirm invisible aviso returns 404
- **WHEN** a user sends POST /api/v1/avisos/{id}/confirmar
- **AND** the aviso is soft-deleted, inactive, or outside visibility window
- **THEN** the system returns 404 Not Found

### Requirement: User can see their pending acknowledgments
The system SHALL return a list of visible avisos where requiere_ack=true and the user has NOT confirmed yet.

#### Scenario: List pending confirms
- **WHEN** an ALUMNO sends GET /api/v1/avisos/pendientes
- **THEN** the system returns a list of avisos that are visible, require_ack=true, and the user has not confirmed

#### Scenario: No pending confirms
- **WHEN** a user has confirmed all visible avisos that require ack
- **THEN** GET /api/v1/avisos/pendientes returns an empty list

### Requirement: Coordinator/Admin can see acknowledgment stats for an aviso
The system SHALL return derived statistics for a specific aviso: total de usuarios alcanzados, total de confirmaciones, and pending (total - confirmations). This endpoint requires `avisos:publicar` permission.

#### Scenario: Get ack stats
- **WHEN** a COORDINADOR sends GET /api/v1/avisos/{id}/stats
- **THEN** the system returns { "total_usuarios_alcanzados": N, "total_confirmaciones": M, "pendientes": N-M }

#### Scenario: Get ack stats without permission
- **WHEN** an ALUMNO sends GET /api/v1/avisos/{id}/stats
- **THEN** the system returns 403 Forbidden
