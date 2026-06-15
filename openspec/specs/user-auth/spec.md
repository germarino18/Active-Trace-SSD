## ADDED Requirements

### Requirement: User model with tenant isolation
The system SHALL define a `User` SQLAlchemy model with the following columns, inheriting from the project's DeclarativeBase (UUID PK, tenant_id, timestamps, soft delete):
- `email`: VARCHAR(255), NOT NULL. Unique per tenant (unique constraint on (tenant_id, email) where deleted_at IS NULL).
- `password_hash`: VARCHAR(255), NOT NULL. Argon2id hash.
- `display_name`: VARCHAR(255), NOT NULL.
- `is_active`: BOOLEAN, NOT NULL, default TRUE.
- `roles`: ARRAY(VARCHAR(50)), NOT NULL, default empty array.
- `totp_secret`: TEXT, nullable. AES-256-GCM encrypted Base32 TOTP secret.
- `totp_enabled_at`: TIMESTAMPTZ, nullable. Set when 2FA enrollment verification succeeds.
- `created_by_id`: UUID, nullable (FK to self — who created this user).
- `updated_by_id`: UUID, nullable (FK to self).

#### Scenario: Create user with required fields
- **WHEN** creating a User with valid email "user@example.com", password_hash (Argon2id), display_name "John Doe", tenant_id, and roles ["ALUMNO"]
- **THEN** the user is persisted with a UUID id, auto-generated timestamps, is_active=TRUE, and roles=["ALUMNO"]

#### Scenario: Email unique per tenant
- **WHEN** creating two users with the same email "dup@example.com" under the same tenant where the first is NOT soft-deleted
- **THEN** the second creation raises an integrity error due to the partial unique index on (tenant_id, email) WHERE deleted_at IS NULL

#### Scenario: Same email allowed across tenants
- **WHEN** creating two users with the same email "dup@example.com" under different tenants
- **THEN** both creations succeed because the unique constraint is scoped to (tenant_id, email)

#### Scenario: Email uniqueness allows reuse after soft delete
- **WHEN** creating a user with email "old@example.com", soft-deleting it, then creating another user with email "old@example.com" under the same tenant
- **THEN** the second creation succeeds

### Requirement: Password hashing with Argon2id
The system SHALL hash all passwords using Argon2id with recommended parameters (memory_cost=19456KiB, time_cost=2, parallelism=1). The hash output includes the algorithm, parameters, salt, and hash in a single string.

#### Scenario: Hash password returns Argon2id string
- **WHEN** hashing a plaintext password "SecureP@ss1"
- **THEN** the result starts with "$argon2id$" and is a single storable string

#### Scenario: Verify correct password
- **WHEN** verifying "SecureP@ss1" against its stored Argon2id hash
- **THEN** verification returns True

#### Scenario: Verify incorrect password
- **WHEN** verifying "WrongP@ss1" against a stored Argon2id hash of "SecureP@ss1"
- **THEN** verification returns False

### Requirement: POST /api/auth/authenticate (Phase 1 of login)
The system SHALL provide an endpoint that accepts `email` and `password`, validates credentials, and returns one of:
- If 2FA is NOT enabled: `200 OK` with `access_token`, `refresh_token`, `token_type: "bearer"`, `expires_in`
- If 2FA IS enabled: `200 OK` with `challenge_token` (5min JWT, single-use), `requires_2fa: true`

This endpoint is subject to rate limiting.

#### Scenario: Login success without 2FA
- **WHEN** calling POST /api/auth/authenticate with valid email and password for a user WITHOUT 2FA enabled
- **THEN** the response is 200 with access_token, refresh_token, token_type "bearer", and expires_in; NOT challenge_token

#### Scenario: Login with valid credentials but 2FA enabled
- **WHEN** calling POST /api/auth/authenticate with valid email and password for a user WITH 2FA enabled
- **THEN** the response is 200 with challenge_token, requires_2fa=true; NO access_token or refresh_token

#### Scenario: Login with invalid password
- **WHEN** calling POST /api/auth/authenticate with valid email but wrong password
- **THEN** the response is 401 Unauthorized with error message "Invalid credentials"

#### Scenario: Login with non-existent email
- **WHEN** calling POST /api/auth/authenticate with an email that does not exist
- **THEN** the response is 401 Unauthorized with error message "Invalid credentials" (no user enumeration)

#### Scenario: Login with inactive user
- **WHEN** calling POST /api/auth/authenticate with valid credentials for a user where is_active=FALSE
- **THEN** the response is 403 Forbidden with error message "Account is disabled"

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

### Requirement: Identity cannot be overridden by request parameters
The system SHALL reject any attempt to supply `user_id`, `tenant_id`, or `roles` via request body, query parameters, or headers (for authentication purposes). The sole source of identity is the verified JWT.

#### Scenario: Extra user_id in request body is ignored
- **WHEN** calling any authenticated endpoint with a valid token AND a `user_id` field in the request body
- **THEN** the system processes the request using the identity from the token, ignoring the body parameter (no error — the parameter is simply not consumed by auth logic)

### Requirement: POST /api/auth/login (2FA Phase 2 — complete login)
The system SHALL provide an endpoint that accepts `challenge_token` and `totp_code`. If both are valid, it issues the real JWT access + refresh pair and marks the challenge token as consumed.

#### Scenario: Complete 2FA login with valid TOTP
- **WHEN** calling POST /api/auth/login with a valid challenge_token and correct totp_code
- **THEN** the response is 200 with access_token, refresh_token, token_type "bearer", expires_in

#### Scenario: Complete 2FA login with invalid TOTP
- **WHEN** calling POST /api/auth/login with a valid challenge_token but incorrect totp_code
- **THEN** the response is 401 Unauthorized

#### Scenario: Reuse of challenge token
- **WHEN** calling POST /api/auth/login twice with the same challenge_token
- **THEN** the first call succeeds, the second call returns 401 Unauthorized

#### Scenario: Expired challenge token
- **WHEN** calling POST /api/auth/login with an expired challenge_token (past 5min TTL)
- **THEN** the response is 401 Unauthorized
