## MODIFIED Requirements

### Requirement: FastAPI dependency get_current_user
The system SHALL provide a `get_current_user` FastAPI dependency that:
1. Extracts the Bearer token from the Authorization header
2. Validates the JWT (signature, expiration, not blacklisted at claim level)
3. Extracts `sub` (user_id UUID), `tenant_id`, `roles` from claims
4. Sets `TenantContext` with the tenant_id
5. Returns the user_id and roles as a `CurrentUser` Pydantic model

The `roles` carried in `CurrentUser` originate from the user's Vigente asignaciones (derived at token issuance), NOT from the deprecated `users.roles` column. The dependency reads the already-derived `roles` claim from the verified JWT.

#### Scenario: Valid token returns current user
- **WHEN** calling a protected endpoint with a valid non-expired access token
- **THEN** get_current_user returns the CurrentUser with correct user_id, tenant_id, and roles from the token claims

#### Scenario: Roles reflect Vigente asignaciones
- **WHEN** a user authenticates and receives a token whose `roles` claim was derived from Vigente asignaciones
- **THEN** `CurrentUser.roles` equals that derived set, used by `require_permission` for fine-grained checks

#### Scenario: Missing Authorization header
- **WHEN** calling a protected endpoint without an Authorization header
- **THEN** the response is 401 Unauthorized

#### Scenario: Expired access token
- **WHEN** calling a protected endpoint with an expired access token
- **THEN** the response is 401 Unauthorized with error "Token has expired"

#### Scenario: Invalid signature
- **WHEN** calling a protected endpoint with a token signed by a different key
- **THEN** the response is 401 Unauthorized with error "Invalid token"

#### Scenario: Tenant context is set from JWT
- **WHEN** get_current_user successfully validates a token
- **THEN** TenantContext.get() returns the tenant_id from the JWT claims
