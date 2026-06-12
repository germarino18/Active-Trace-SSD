## ADDED Requirements

### Requirement: JWT access token structure
The system SHALL issue JWT access tokens signed with HS256 (or RS256 for multi-service future) with the following claims:
- `sub`: user UUID (string)
- `tenant_id`: tenant UUID (string)
- `roles`: array of role strings (e.g., `["ADMIN", "PROFESOR"]`)
- `exp`: expiration timestamp (30 minutes from issuance)
- `iat`: issued-at timestamp
- `jti`: unique token ID (UUID) for log correlation
Permissions are NOT stored in the JWT — resolved server-side from roles.

#### Scenario: Issued access token has correct claims
- **WHEN** issuing an access token for a user with a given tenant_id and roles
- **THEN** the decoded token has sub, tenant_id, roles, exp, iat, and jti; exp is 30 minutes from iat

#### Scenario: Access token is valid for exactly 30 minutes

- **WHEN** issuing an access token
- **THEN** exp is exactly 1800 seconds (30 minutes) after iat
#### Scenario: Access token verifies signature
- **WHEN** verifying an access token signed with the correct secret
- **THEN** verification passes and returns the decoded claims

#### Scenario: Tampered access token is rejected
- **WHEN** verifying an access token whose payload has been modified
- **THEN** verification fails with an invalid signature error

### Requirement: Refresh token structure and storage
The system SHALL issue opaque refresh tokens (random UUID v4) stored in a `refresh_tokens` table with:
- `id`: UUID PK
- `user_id`: UUID, FK → users.id, NOT NULL
- `token_hash`: VARCHAR(64), NOT NULL — SHA-256 of the raw refresh token
- `device_info`: VARCHAR(255), nullable — client-reported device name
- `expires_at`: TIMESTAMPTZ, NOT NULL — 30 days from issuance
- `created_at`: TIMESTAMPTZ, NOT NULL
- `revoked_at`: TIMESTAMPTZ, nullable
- `replaced_by`: UUID, nullable — FK self-reference to the token that replaced this one during rotation

This table does NOT have tenant_id — refresh tokens are scoped to user, not tenant (a user belongs to one tenant anyway, and logout should work regardless of tenant context).

#### Scenario: Issue refresh token stores hashed token
- **WHEN** issuing a refresh token for a user
- **THEN** the raw token is returned to the client; the database stores SHA-256(token_raw), NOT the raw token

#### Scenario: Refresh token has 30-day expiration
- **WHEN** issuing a refresh token
- **THEN** expires_at is set to 30 days from created_at

### Requirement: POST /api/auth/refresh — token rotation
The system SHALL provide `POST /api/auth/refresh` that:
1. Validates the raw refresh token (find by hash, check not revoked, check not expired)
2. Revokes the old token (set `revoked_at`)
3. Issues a new access + refresh pair
4. Links `replaced_by` on the old token to the new token's ID

If a revoked refresh token is presented (theft detection), ALL refresh tokens for that user are revoked immediately.

#### Scenario: Successful token refresh
- **WHEN** calling POST /api/auth/refresh with a valid, non-expired, non-revoked refresh token
- **THEN** the response is 200 with a new access_token and refresh_token; the old refresh token has revoked_at set

#### Scenario: Refresh with revoked token triggers theft protection
- **WHEN** calling POST /api/auth/refresh with a previously revoked refresh token
- **THEN** ALL refresh tokens for that user are revoked; the response is 401 Unauthorized

#### Scenario: Refresh with expired token
- **WHEN** calling POST /api/auth/refresh with a refresh token past its expires_at
- **THEN** the response is 401 Unauthorized

#### Scenario: Refresh with non-existent token
- **WHEN** calling POST /api/auth/refresh with a random UUID that does not match any stored hash
- **THEN** the response is 401 Unauthorized

### Requirement: POST /api/auth/logout — session revocation
The system SHALL provide `POST /api/auth/logout` that accepts a refresh token and revokes it (sets `revoked_at`). This endpoint requires a valid access token (authenticated via `get_current_user`).

#### Scenario: Successful logout
- **WHEN** calling POST /api/auth/logout with a valid access token and a valid refresh token in the body
- **THEN** the refresh token is revoked (revoked_at set) and the response is 200 OK

#### Scenario: Logout without authentication
- **WHEN** calling POST /api/auth/logout without a valid access token
- **THEN** the response is 401 Unauthorized before any revocation happens

### Requirement: Rate limiting on login endpoint
The system SHALL limit POST /api/auth/authenticate to 5 attempts per 60 seconds per unique (IP, email) combination. When the limit is exceeded, the endpoint returns 429 Too Many Requests with a `Retry-After` header indicating seconds until the window resets.

The rate limiter uses an in-memory sliding window counter. It is NOT bypassed by valid credentials — the counter increments on every login attempt, successful or not.

#### Scenario: Under rate limit, request proceeds
- **WHEN** calling POST /api/auth/authenticate 4 times within 60 seconds from the same IP and email
- **THEN** all 4 requests are processed normally (200 or 401 depending on credentials)

#### Scenario: Rate limit exceeded
- **WHEN** calling POST /api/auth/authenticate for the 6th time within 60 seconds from the same IP and email
- **THEN** the response is 429 Too Many Requests with a Retry-After header

#### Scenario: Different email under same IP is independent
- **WHEN** 5 attempts from IP 1.2.3.4 with email "a@x.com" exhaust the limit, then attempting with email "b@x.com" from the same IP
- **THEN** the request for "b@x.com" is processed normally (not rate-limited)

#### Scenario: Rate limit window resets after 60 seconds
- **WHEN** rate limit is exceeded at time T, and a new request arrives at T+61s from the same IP and email
- **THEN** the request is processed normally (the window has reset)

### Requirement: Anonymous routes are explicitly marked
Only the following routes are anonymous (no auth required):
- POST /api/auth/authenticate
- POST /api/auth/login (2FA Phase 2)
- POST /api/auth/forgot
- POST /api/auth/reset

All other routes in the API require a valid access token. The auth router MUST explicitly annotate which routes are public vs authenticated.

#### Scenario: Anonymous routes are accessible without token
- **WHEN** calling any anonymous route without an Authorization header
- **THEN** the request is processed normally (no 401 error)

#### Scenario: Protected routes reject anonymous requests
- **WHEN** calling any non-anonymous route without an Authorization header
- **THEN** the response is 401 Unauthorized
