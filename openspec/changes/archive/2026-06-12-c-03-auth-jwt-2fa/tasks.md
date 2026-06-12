## 1. Foundation — Models, Migrations, and Dependencies

- [x] 1.1 Install new dependencies: `pyotp`, `itsdangerous` (or `python-jose[cryptography]` for JWT — check if already present)
- [x] 1.2 Create `User` SQLAlchemy model in `app/models/user.py` with: id (UUID PK from BaseMixin), tenant_id (FK → tenant.id), email (VARCHAR 255), password_hash (VARCHAR 255), display_name (VARCHAR 255), is_active (BOOLEAN default TRUE), roles (ARRAY(VARCHAR)), totp_secret (TEXT nullable), totp_enabled_at (TIMESTAMPTZ nullable), created_by_id (UUID nullable FK → users.id), updated_by_id (UUID nullable FK → users.id). Inherit from DeclarativeBase.
- [x] 1.3 Add partial unique index on `(tenant_id, email) WHERE deleted_at IS NULL` on the User model
- [x] 1.4 Create `RefreshToken` model in `app/models/refresh_token.py` with: id (UUID PK), user_id (UUID FK → users.id), token_hash (VARCHAR 64), device_info (VARCHAR 255 nullable), expires_at (TIMESTAMPTZ), created_at (TIMESTAMPTZ), revoked_at (TIMESTAMPTZ nullable), replaced_by (UUID nullable FK → refresh_tokens.id)
- [x] 1.5 Create `RecoveryToken` model in `app/models/recovery_token.py` with: id (UUID PK), user_id (UUID FK → users.id), token_hash (VARCHAR 64), expires_at (TIMESTAMPTZ), used_at (TIMESTAMPTZ nullable), created_at (TIMESTAMPTZ)
- [x] 1.6 Generate Alembic migration for users, refresh_tokens, recovery_tokens tables
- [x] 1.7 Create `UserRepository` in `app/repositories/user_repository.py` with find_by_email(tenant_id, email), find_by_id, create, update
- [x] 1.8 Create `RefreshTokenRepository` in `app/repositories/refresh_token_repository.py` with create, find_by_hash, revoke, revoke_all_for_user. This repository bypasses tenant scoping (tokens are cross-tenant by nature).
- [x] 1.9 Create `RecoveryTokenRepository` in `app/repositories/recovery_token_repository.py` with create, find_by_hash, mark_used, revoke_all_for_user

## 2. Security and Utility Services

- [x] 2.1 Create `PasswordService` in `app/services/auth/password_service.py` with `hash_password(plain: str) -> str` (Argon2id) and `verify_password(plain: str, hash: str) -> bool`
- [x] 2.2 Create `TokenService` in `app/services/auth/token_service.py` with:
    - `create_access_token(user: User) -> str`: JWT with sub, tenant_id, roles, exp=30min, iat, jti (UUID)
    - `verify_access_token(token: str) -> dict`: verify signature + expiration, return claims
    - `generate_refresh_token() -> tuple[str, str]`: returns (raw_token, sha256_hash)
    - `create_challenge_token(user: User) -> str`: JWT with sub, tenant_id, purpose="2fa_challenge", exp=5min
    - `verify_challenge_token(token: str) -> dict`: verify signature + purpose + expiration
- [x] 2.3 Create `RateLimiter` in `app/services/auth/rate_limiter.py`: in-memory sliding window with key=(ip, email), max_attempts=5, window_seconds=60. Thread-safe.
- [x] 2.4 Create `TwoFactorService` in `app/services/auth/two_factor_service.py` with:
    - `generate_secret() -> dict`: returns secret and QR URI (uses pyotp)
    - `verify_code(secret: str, code: str) -> bool`: validates TOTP code (window=1)
    - `encrypt_secret(secret: str) -> str`: AES-256-GCM encrypt
    - `decrypt_secret(encrypted: str) -> str`: AES-256-GCM decrypt
- [x] 2.5 Create `PasswordRecoveryService` in `app/services/auth/password_recovery_service.py` with:
    - `generate_recovery_token(user: User) -> str`: generates 32-byte URL-safe token, stores hash
    - `validate_recovery_token(raw_token: str) -> User`: finds by hash, checks expired/used, returns user
    - `complete_reset(user: User, new_password: str)`: updates password hash, revokes all refresh tokens

## 3. FastAPI Dependencies and Middleware

- [x] 3.1 Create `get_current_user` dependency in `app/api/dependencies/auth.py`:
    - Extract Bearer token from Authorization header
    - Call TokenService.verify_access_token()
    - Extract sub, tenant_id, roles from claims
    - Set TenantContext with tenant_id
    - Return CurrentUser Pydantic model (user_id: UUID, tenant_id: UUID, roles: list[str])
- [x] 3.2 Create rate limiter dependency that wraps the RateLimiter service and can be injected into routes
- [x] 3.3 Update `get_tenant_id()` in tenant-resolution to first check JWT claims (via TenantContext), then fall back to X-Tenant-ID header (backward compat until all routes use auth)

## 4. Auth Router — Endpoints

- [x] 4.1 Create `app/api/routers/auth.py` with the auth router. Tag: "auth". Prefix: /api/auth. Mark anonymous routes explicitly.
- [x] 4.2 Implement `POST /api/auth/authenticate` (anonymous):
    - Apply rate limiter dependency
    - Validate email + password via PasswordService
    - If invalid, increment rate counter → 401
    - If user inactive → 403
    - If 2FA enabled → return challenge_token (5min JWT), requires_2fa=true
    - If 2FA NOT enabled → return access_token + refresh_token pair
- [x] 4.3 Implement `POST /api/auth/login` (anonymous — 2FA Phase 2):
    - Accept challenge_token + totp_code
    - Validate challenge_token via TokenService
    - Decrypt totp_secret, verify TOTP code via TwoFactorService
    - Issue real access_token + refresh_token pair
- [x] 4.4 Implement `POST /api/auth/refresh` (anonymous):
    - Accept raw refresh token
    - Find by hash via RefreshTokenRepository
    - If revoked → trigger theft protection (revoke ALL for user) → 401
    - If expired → 401
    - Issue new pair, revoke old token, link replaced_by
- [x] 4.5 Implement `POST /api/auth/logout` (authenticated via get_current_user):
    - Accept refresh token in body
    - Revoke it via RefreshTokenRepository
    - Return 200
- [x] 4.6 Implement `POST /api/auth/2fa/enroll` (authenticated):
    - Check 2FA not already enabled → 409 if enabled
    - Generate secret via TwoFactorService
    - Encrypt and store totp_secret
    - Return secret + qr_uri (plaintext secret, one-time display)
- [x] 4.7 Implement `POST /api/auth/2fa/verify` (authenticated):
    - Check totp_secret exists → 400 if no pending enrollment
    - Verify totp_code via TwoFactorService
    - Set totp_enabled_at = now()
    - Return 200
- [x] 4.8 Implement `POST /api/auth/2fa/disable` (authenticated):
    - Accept password + totp_code
    - Validate password via PasswordService
    - Decrypt secret, verify TOTP code
    - Clear totp_secret and totp_enabled_at
    - Return 200
- [x] 4.9 Implement `POST /api/auth/forgot` (anonymous):
    - Accept email
    - Find user by email; if found and active, generate recovery token
    - Always return 200 (no email enumeration)
- [x] 4.10 Implement `POST /api/auth/reset` (anonymous):
    - Accept token + new_password + new_password_confirm
    - Validate passwords match
    - Validate token via PasswordRecoveryService
    - Update password hash
    - Mark token used
    - Revoke all refresh tokens for user
    - Return 200

## 5. Testing

- [x] 5.1 Write tests for User model: create, email uniqueness per tenant, same email across tenants, soft delete reuse
- [x] 5.2 Write tests for PasswordService: hash returns argon2id string, verify correct, verify incorrect
- [x] 5.3 Write tests for TokenService: access token creation and verification, expiration, tamper detection, challenge token creation and verification
- [x] 5.4 Write tests for RefreshToken flow: issue, refresh success, rotation (old revoked), theft detection (revoked reuse invalidates all)
- [x] 5.5 Write tests for RateLimiter: under limit passes, over limit blocks, different email same IP independent, window resets
- [x] 5.6 Write tests for TwoFactorService: secret generation returns valid Base32, verify correct code, verify incorrect code, verify adjacent window
- [x] 5.7 Write tests for for 2FA endpoints: enroll, verify, disable, enrollment flow (enroll → verify → login)
- [x] 5.8 Write tests for password recovery: forgot creates token, reset with valid token, used/expired token rejected, all sessions revoked after reset
- [x] 5.9 Write tests for login endpoint: success without 2FA, success with 2FA (full 2-phase flow), invalid credentials, inactive user, challenge token reuse prevention
- [x] 5.10 Write tests for get_current_user: valid token returns correct identity, missing/expired/invalid token returns 401, identity immutable (extra user_id in body ignored)

## 6. Integration and Final Wiring

- [x] 6.1 Register auth router in the main FastAPI app
- [x] 6.2 Set up JWT_SECRET_KEY in app configuration (from env, minimum 256-bit)
- [x] 6.3 Ensure all existing routes are reviewed: any that should be authenticated now get get_current_user dependency
- [x] 6.4 Run full test suite, verify ≥80% line coverage and ≥90% business rule coverage
- [x] 6.5 Run linting and type checking
