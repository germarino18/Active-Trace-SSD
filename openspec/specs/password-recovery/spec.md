## ADDED Requirements

### Requirement: POST /api/auth/forgot — request password reset
The system SHALL provide an anonymous endpoint accepting `email`. If the email corresponds to an active user, the system generates a single-use recovery token (32 bytes, URL-safe base64 encoded), stores its SHA-256 hash in the `recovery_tokens` table with a 15-minute TTL, and triggers a notification (email stub for MVP). The response is always 200 OK regardless of whether the email exists (to prevent email enumeration).

#### Scenario: Forgot password for existing email
- **WHEN** calling POST /api/auth/forgot with the email of an active user
- **THEN** the response is 200 OK; a recovery token is created and stored (hashed) in recovery_tokens with expires_at = now + 15 minutes

#### Scenario: Forgot password for non-existent email
- **WHEN** calling POST /api/auth/forgot with an email that has no associated user
- **THEN** the response is 200 OK (same as existing email — no email enumeration)

#### Scenario: Forgot password for inactive user
- **WHEN** calling POST /api/auth/forgot with the email of a user whose is_active=FALSE
- **THEN** the response is 200 OK, but no token is created (user cannot recover a disabled account through this flow)

### Requirement: Recovery token model and storage
The system SHALL define a `RecoveryToken` model with:
- `id`: UUID PK
- `user_id`: UUID, FK → users.id, NOT NULL
- `token_hash`: VARCHAR(64), NOT NULL — SHA-256 of the raw token
- `expires_at`: TIMESTAMPTZ, NOT NULL
- `used_at`: TIMESTAMPTZ, nullable
- `created_at`: TIMESTAMPTZ, NOT NULL

#### Scenario: Recovery token is stored hashed
- **WHEN** creating a recovery token
- **THEN** the database stores SHA-256(token_raw), NOT the raw token value

#### Scenario: Recovery token has 15-minute TTL
- **WHEN** creating a recovery token
- **THEN** expires_at is exactly 15 minutes from created_at

### Requirement: POST /api/auth/reset — complete password reset
The system SHALL provide an anonymous endpoint accepting `token`, `new_password`, and `new_password_confirm`. It validates:
1. The token hash exists and is not used
2. The token is not expired
3. `new_password` matches `new_password_confirm`
4. `new_password` meets minimum length (8 characters)

If valid, the user's password is updated to the new Argon2id hash, the token is marked as used (`used_at`), and ALL refresh tokens for that user are revoked.

#### Scenario: Successful password reset
- **WHEN** calling POST /api/auth/reset with a valid recovery token, new_password="NewStr0ng!", and matching confirmation
- **THEN** the response is 200 OK; the user's password_hash is updated to the new Argon2id hash; the token's used_at is set; ALL refresh tokens for that user are revoked

#### Scenario: Reset with mismatched passwords
- **WHEN** calling POST /api/auth/reset with a valid token but new_password and new_password_confirm do not match
- **THEN** the response is 422 Unprocessable Entity with validation error

#### Scenario: Reset with short password
- **WHEN** calling POST /api/auth/reset with a valid token but new_password="abc" (less than 8 characters)
- **THEN** the response is 422 Unprocessable Entity with validation error

#### Scenario: Reset with used token
- **WHEN** calling POST /api/auth/reset with a token that already has used_at set
- **THEN** the response is 401 Unauthorized

#### Scenario: Reset with expired token
- **WHEN** calling POST /api/auth/reset with a token past its expires_at
- **THEN** the response is 401 Unauthorized

#### Scenario: Reset with non-existent token
- **WHEN** calling POST /api/auth/reset with a random string that does not match any stored token hash
- **THEN** the response is 401 Unauthorized

### Requirement: Password reset revokes all sessions
When a password reset is successful, ALL refresh tokens for that user MUST be revoked. This ensures that any active session (including potentially attacker-controlled ones) is invalidated.

#### Scenario: All refresh tokens revoked after reset
- **WHEN** a user completes a password reset
- **THEN** querying refresh_tokens for that user shows revoked_at set on all previously valid tokens
