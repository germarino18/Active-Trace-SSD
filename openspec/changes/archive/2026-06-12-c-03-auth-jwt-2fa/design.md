## Context

activia-trace currently has no user authentication. The foundation layers (C-01 tenant model, C-02 repository base) are in place, but there is no concept of users, sessions, or identity. The system currently resolves tenant via `X-Tenant-ID` header (a temporary arrangement documented in tenant-resolution spec). This change introduces the identity layer: user model, JWT-based auth with refresh rotation, optional 2FA TOTP, password recovery, and a `get_current_user` dependency that will gate every protected endpoint.

Security governance is CRITICAL. Identity, roles, and tenant MUST come exclusively from the verified JWT — never from request parameters. All domain rules from knowledge-base files (03_actores_y_roles.md §1, 08_arquitectura_propuesta.md §3.3) enforce this.

## Goals / Non-Goals

**Goals:**
- User registration of identity (email + password) with multi-tenant isolation (email unique per tenant)
- Secure credential validation with Argon2id password hashing
- JWT access token (30min TTL, stateless) + refresh token (opaque, server-tracked, rotation on use)
- Optional 2FA TOTP per user with enrollment, verification, and disablement flows
- Password recovery with single-use tokens and email dispatch
- Rate limiting on login: 5 attempts / 60s per IP+email combination
- FastAPI dependency `get_current_user` that resolves user_id, tenant_id, and roles from verified JWT and sets TenantContext
- Refresh token blacklist (server-side table) for explicit logout

**Non-Goals:**
- OAuth2 / social login / SSO (Moodle SSO deferred to future change — ADR-001)
- User registration endpoints (sign-up is by invitation/admin — not part of this change)
- Fine-grained permission resolution (permissions are resolved server-side from roles; not stored in JWT)
- Email delivery implementation (email sending is a stub/placeholder until communication module exists)
- Password complexity policy enforcement beyond minimum length (deferred)
- Account lockout beyond rate limiting (deferred)

## Decisions

### D1: JWT access token is stateless; refresh token is server-tracked
Access tokens (30min TTL) carry `sub` (user_id UUID), `tenant_id`, `roles`, `exp`. They are NOT stored server-side — validation is purely cryptographic signature check. Refresh tokens are opaque UUIDs stored in `refresh_tokens` table with `user_id`, `token_hash` (SHA-256 of the raw token), `device_info`, `expires_at`, `revoked_at`. On refresh, the old token is revoked (rotation) and a new pair is issued.

**Rationale**: 30-minute TTL balances user experience (fewer refreshes during active sessions) with security (tokens remain short-lived enough to limit revocation window). Server-tracked refresh tokens enable explicit logout and rotation detection. If a reused (stale) refresh token is presented, ALL tokens for that user are revoked (token theft detection).

**Alternatives considered**:
- Stateless refresh tokens (opaque but not stored): Cannot revoke sessions or detect theft. Rejected.
- Access+refresh both in DB: Adds latency to every request. Rejected.

### D2: TOTP secret encrypted with AES-256 at rest
The `totp_secret` column in `users` stores the Base32-encoded TOTP secret encrypted with AES-256-GCM using the project's encryption service from `aes-encryption` spec. `totp_enabled_at` timestamp is set only after successful enrollment verification.

**Rationale**: TOTP secrets are sensitive — an attacker with DB access could impersonate any user. Encryption follows the project-wide PII protection policy.

**Alternatives considered**:
- Plaintext storage: Simpler but violates security rules (secretos y PII siempre AES-256).
- Hash + compare for TOTP: TOTP verification requires the raw secret. Encryption is the correct approach.

### D3: Login flow has two phases when 2FA is enabled
Phase 1: validate email + password. If 2FA is NOT enabled, issue tokens immediately. If 2FA IS enabled, issue a temporary "2FA challenge token" (5min TTL, single-use, includes `user_id` and `tenant_id`). Phase 2: validate TOTP code + challenge token → issue real tokens.

**Rationale**: Separates credential verification from OTP verification. The challenge token is NOT a session — it only proves phase 1 passed. This prevents OTP brute-force without valid credentials. The challenge token is a signed JWT with `purpose: 2fa_challenge`, minimal surface.

**Alternatives considered**:
- Single endpoint returning `2fa_required`: Requires client state management. The two-phase approach with a challenge token is more secure and REST-friendly.
- Issuing partial session: Would require session state before auth is complete. Rejected.

### D4: Rate limiting at the application layer (FastAPI middleware/dependency)
In-memory sliding window counter keyed by `ip:email`. 5 attempts per 60s window. Returns 429 Too Many Requests with `Retry-After` header when exceeded.

**Rationale**: Application-layer rate limiting is simpler and faster to implement than infrastructure-level (nginx, etc.) for this use case. In-memory (not Redis) keeps infra minimal for MVP. If horizontal scaling is needed, Redis-backed rate limiting is a drop-in replacement.

**Alternatives considered**:
- Redis-backed: Premature infrastructure dependency for MVP.
- Database-backed: Adds too much latency to login path.

### D5: Recovery tokens are single-use, short TTL, stored hashed
Recovery tokens use `secrets.token_urlsafe(32)` and are stored as SHA-256 hashes in `recovery_tokens` table with `user_id`, `expires_at` (15min), and `used_at`. Once used or expired, they cannot be reused.

**Rationale**: Hash-at-rest prevents DB-read attacks. Short TTL limits exposure window. Single-use per spec (06_funcionalidades.md).

**Alternatives considered**:
- JWT as recovery token: Overkill for a single-use flow, harder to revoke.
- Plaintext storage: Violates security rules.

### D6: Tenant resolved from JWT, not from request
After login, all subsequent requests carry the access token. The `get_current_user` dependency extracts `tenant_id` from the JWT claims and sets `TenantContext`. The old `X-Tenant-ID` header fallback in `get_tenant_id()` is superseded when a valid JWT is present.

**Rationale**: Regla de oro — identity and tenant come ONLY from verified JWT. This eliminates a common multi-tenant attack vector (tenant hopping via header manipulation).

### D7: Password reset requires confirmation of new password
The `POST /api/auth/reset` endpoint accepts `token`, `new_password`, and `new_password_confirm`. This prevents accidental lockouts from typoed passwords. Validation is server-side.

## Risks / Trade-offs

- **[Risk] Token theft via refresh token leak**: If a refresh token is intercepted, the attacker can issue new tokens for 30 days.
  - **Mitigation**: Rotation on every refresh (old token revoked). Token theft detection: if a revoked token is reused, ALL sessions for that user are revoked.
- **[Risk] Rate limiting bypass via IP rotation**: An attacker using a botnet can spread attempts across IPs.
  - **Mitigation**: Acceptable risk at MVP scale. Future enhancement: add email-based exponential backoff.
- **[Risk] Email delivery dependency for password recovery**: If email is down, users cannot reset passwords.
  - **Mitigation**: Recovery is logged server-side; support staff can manually trigger via admin endpoint in future.
- **[Risk] 2FA lockout**: User loses TOTP device and cannot authenticate.
  - **Mitigation**: Recovery codes (future). Support staff can disable 2FA after identity verification (admin endpoint).
- **[Risk] In-memory rate limiter lost on restart**: Sliding window counters reset, allowing burst after restart.
  - **Mitigation**: Acceptable for MVP. Migration to Redis eliminates this.
- **[Trade-off] Stateless access tokens cannot be individually revoked**: Revocation is at the refresh token level (logout) or all-sessions level (password change).
  - **Rationale**: 15min TTL makes this acceptable. The window is small.
