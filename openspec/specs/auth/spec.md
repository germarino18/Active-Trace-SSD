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
- **THEN** the system calls POST `/api/auth/verify-2fa` with the challenge token and TOTP code
- **THEN** the system returns the access token, refresh token, and user profile
- **THEN** the system stores the access token in memory and navigates to the home page

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
- **THEN** the system calls POST `/api/auth/logout`
- **THEN** the system clears the in-memory access token
- **THEN** the system navigates to the login page

### Requirement: Tokens refresh transparently
The system SHALL automatically refresh the access token when it expires, without user intervention.

#### Scenario: Transparent refresh on 401
- **WHEN** the access token expires and the Axios interceptor receives a 401 response
- **THEN** the system calls POST `/api/auth/refresh` using the httpOnly cookie
- **WHEN** refresh succeeds
- **THEN** the system retries the original request with the new access token
- **WHEN** refresh fails (expired or revoked refresh token)
- **THEN** the system clears the session and redirects to login

### Requirement: User can view their profile
The system SHALL display the authenticated user's profile information.

#### Scenario: Profile loaded on auth
- **WHEN** the user is authenticated
- **THEN** the system fetches GET `/api/auth/me` via TanStack Query
- **THEN** the system displays the user's name, email, and roles in the header user menu
