## Why

activia-trace requires a secure authentication system as the foundation for all user-facing features. Without auth, no user can access the system, no tenant isolation can be enforced at the identity level, and no protected operations can be gated. ADR-001 confirms building auth in-house (email + password + optional 2FA TOTP + JWT) rather than integrating Moodle SSO at this stage. This change enables the entire platform stack above it.

## What Changes

- **User model**: `id` (UUID PK), `tenant_id` (FK), `email` (unique per tenant), `password_hash` (Argon2id), `display_name`, `is_active`, `totp_secret` (nullable), `totp_enabled_at` (nullable), roles (array), timestamps, soft delete
- **`POST /api/auth/login`**: Validates email + password (Argon2id), checks optional 2FA TOTP, issues JWT access (30min) + refresh token with rotation
- **`POST /api/auth/refresh`**: Validates refresh token, rotates it (old invalidated), emits new pair
- **`POST /api/auth/logout`**: Revokes the current refresh token (server-side session invalidation)
- **`POST /api/auth/2fa/enroll`**: Generates TOTP secret + QR URI, stores encrypted secret on user
- **`POST /api/auth/2fa/verify`**: Confirms TOTP code, enables 2FA for user
- **`POST /api/auth/2fa/disable`**: Removes TOTP secret, disables 2FA (requires current password)
- **`POST /api/auth/forgot`**: Generates single-use recovery token with short TTL, sends via email
- **`POST /api/auth/reset`**: Validates recovery token, updates password
- **`get_current_user` dependency**: Resolves user identity + tenant + roles from verified JWT
- **Rate limiting**: 5 attempts per 60s per IP+email on login endpoint
- **Token blacklist**: Server-side tracking of revoked refresh tokens and recovery tokens (not JWT access tokens — those are short-lived and stateless per ADR-001)

## Capabilities

### New Capabilities
- `user-auth`: User registration/login model, password hashing (Argon2id), identity verification
- `jwt-tokens`: JWT access + refresh token issuance, validation, rotation, and revocation
- `two-factor-auth`: TOTP enrollment, verification, enforcement, and disablement flow
- `password-recovery`: Forgot/reset flow with single-use tokens and email notification

### Modified Capabilities
- *(none — first auth-related change)*

## Impact

- **New models**: `User`, `RefreshToken`, `RecoveryToken` — new Alembic migration
- **New tables**: `users`, `refresh_tokens`, `recovery_tokens`
- **New repositories**: `UserRepository`, `RefreshTokenRepository`
- **New services**: `AuthService`, `TwoFactorService`, `TokenService`, `PasswordRecoveryService`
- **New endpoints**: 8 new routes under `/api/auth/`
- **New dependencies**: `get_current_user` (FastAPI dependency), rate limiter middleware/dependency
- **New package**: `itsdangerous` or equivalent for recovery tokens, `pyotp` for TOTP
- **Tenant-resolution update**: After C-03, tenant is resolved from JWT rather than `X-Tenant-ID` header
- **Repository-base**: RefreshTokenRepository bypasses tenant scoping (tokens are cross-tenant by design — tied to user+device, not tenant)
