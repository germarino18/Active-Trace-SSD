## MODIFIED Requirements

### Requirement: JWT access token structure
The system SHALL issue JWT access tokens signed with HS256 (or RS256 for multi-service future) with the following claims:
- `sub`: user UUID (string)
- `tenant_id`: tenant UUID (string)
- `roles`: array of role strings (e.g., `["ADMIN", "PROFESOR"]`), derived from the user's alive, Vigente asignaciones (DISTINCT `asignacion.rol`), NOT from `users.roles`
- `exp`: expiration timestamp (30 minutes from issuance)
- `iat`: issued-at timestamp
- `jti`: unique token ID (UUID) for log correlation
Permissions are NOT stored in the JWT — resolved server-side from roles. The `users.roles` column is deprecated and SHALL NOT be read to populate the `roles` claim.

#### Scenario: Issued access token has correct claims
- **WHEN** issuing an access token for a user with a given tenant_id and Vigente asignaciones
- **THEN** the decoded token has sub, tenant_id, roles, exp, iat, and jti; the `roles` claim equals the DISTINCT roles of the user's Vigente asignaciones; exp is 30 minutes from iat

#### Scenario: Expired assignments are excluded from the roles claim
- **WHEN** issuing an access token for a user whose only PROFESOR asignacion is Vencida
- **THEN** the `roles` claim does NOT include PROFESOR

#### Scenario: Access token is valid for exactly 30 minutes
- **WHEN** issuing an access token
- **THEN** exp is exactly 1800 seconds (30 minutes) after iat

#### Scenario: Access token verifies signature
- **WHEN** verifying an access token signed with the correct secret
- **THEN** verification passes and returns the decoded claims

#### Scenario: Tampered access token is rejected
- **WHEN** verifying an access token whose payload has been modified
- **THEN** verification fails with an invalid signature error
