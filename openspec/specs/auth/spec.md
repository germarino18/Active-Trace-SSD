## ADDED Requirements

### Requirement: User can log in with email and password
The system SHALL authenticate a user by accepting their email and password, along with a tenant identifier, and return JWT access and refresh tokens on success.

#### Scenario: Successful login
- **WHEN** the user submits a valid email, password, and X-Tenant-ID header
- **THEN** the system calls POST `/api/auth/authenticate` and returns `access_token` (expires_in 15min), `refresh_token`, and user profile
- **THEN** the system stores the access token in memory and navigates to the home page

#### Scenario: Invalid credentials
- **WHEN** the user submits an incorrect email or password
- **THEN** the system displays a user-visible error message "Credenciales inválidas"

#### Scenario: Unknown tenant
- **WHEN** the user submits a non-existent tenant ID
- **THEN** the system displays a user-visible error message "Tenant no encontrado"

#### Scenario: 2FA required on login
- **WHEN** the backend responds with `requires_2fa: true` and a `challenge_token`
- **THEN** the system renders the 2FA verification form instead of navigating to home

### Requirement: User can verify 2FA with TOTP code
The system SHALL complete authentication when 2FA is enabled by verifying the TOTP code against a challenge token.

#### Scenario: Successful 2FA verification
- **WHEN** the user enters a valid TOTP code and submits
- **THEN** the system calls POST `/api/auth/login` with `{ challenge_token, totp_code }`
- **THEN** the system returns the access token, refresh token, and user profile
- **THEN** the system stores the access token in memory, refresh token in cookie, and navigates to the home page

#### Scenario: Invalid TOTP code
- **WHEN** the user enters an incorrect TOTP code
- **THEN** the system displays a user-visible error message "Código inválido"

### Requirement: User can recover password via email
The system SHALL allow a user to request a password reset email by providing their email address and tenant ID.

#### Scenario: Forgot password request
- **WHEN** the user submits their email and tenant ID on the forgot password page
- **THEN** the system calls POST `/api/auth/forgot`
- **THEN** the system displays a success message "Si el email existe, recibirá un enlace de recuperación"

#### Scenario: Reset password with token
- **WHEN** the user navigates to the reset password page with a valid token
- **THEN** the system renders a form for the new password and confirmation
- **WHEN** the user submits a valid new password and confirmation
- **THEN** the system calls POST `/api/auth/reset` with the token and new password
- **THEN** the system displays a success message and redirects to login

### Requirement: User can log out
The system SHALL terminate the current session on logout.

#### Scenario: Successful logout
- **WHEN** the user clicks "Cerrar sesión" in the user menu
- **THEN** the system calls POST `/api/auth/logout` with `{ refresh_token }` in the body
- **THEN** the system clears the in-memory access token, refresh token, and deletes both session cookies (`js-trace-tenant`, `js-trace-rt`)
- **THEN** the system navigates to the login page

### Requirement: Tokens refresh transparently
The system SHALL automatically refresh the access token when it expires, without user intervention. The refresh token SHALL be sent in the request body (not as a cookie).

#### Scenario: Transparent refresh on 401
- **WHEN** the access token expires and the Axios interceptor receives a 401 response
- **THEN** the system calls POST `/api/auth/refresh` with `{ refresh_token }` in the body
- **WHEN** refresh succeeds
- **THEN** the system stores the new access token in memory, the new refresh token in the `js-trace-rt` cookie, and retries the original request
- **WHEN** refresh fails (expired or revoked refresh token)
- **THEN** the system clears the session, deletes both cookies, and redirects to login

#### Scenario: Session restored on mount when cookies exist
- **WHEN** `AuthProvider` mounts and both `js-trace-tenant` and `js-trace-rt` cookies are present
- **THEN** the system reads both cookies, sets the tenant header and refresh token in memory, and calls POST `/api/auth/refresh`
- **WHEN** refresh succeeds
- **THEN** the system fetches `GET /api/auth/me` and sets session status to `authenticated`
- **WHEN** refresh fails
- **THEN** the system deletes both cookies and sets session status to `unauthenticated`

#### Scenario: Session not attempted when cookies are absent on mount
- **WHEN** `AuthProvider` mounts and either `js-trace-tenant` or `js-trace-rt` cookie is absent
- **THEN** the system immediately sets session status to `unauthenticated` without calling the refresh endpoint

### Requirement: User can view their profile
The system SHALL display the authenticated user's profile information.

#### Scenario: Profile loaded on auth
- **WHEN** the user is authenticated
- **THEN** the system fetches GET `/api/auth/me` via TanStack Query
- **THEN** the system displays the user's name, email, and roles in the header user menu
