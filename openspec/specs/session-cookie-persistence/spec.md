## ADDED Requirements

### Requirement: Tenant ID persists across page reloads via session cookie
The system SHALL save the tenant ID in a browser session cookie (`js-trace-tenant`) at login time so the session can be restored after a page reload without requiring the user to log in again.

#### Scenario: Tenant cookie is set on login
- **WHEN** the user successfully authenticates with a tenant ID (direct login or 2FA)
- **THEN** the system SHALL write the tenant ID to a cookie named `js-trace-tenant`
- **THEN** the cookie SHALL have `SameSite=Strict` and `Secure` attributes
- **THEN** the cookie SHALL be a session cookie (no `Max-Age` or `Expires`) so it expires when the browser is closed

#### Scenario: Tenant cookie is cleared on logout
- **WHEN** the user logs out or the refresh token is rejected by the backend
- **THEN** the system SHALL delete the `js-trace-tenant` cookie
- **THEN** the system SHALL clear the in-memory access token and navigate to login

#### Scenario: Session is restored after page reload when cookie exists
- **WHEN** the user reloads the page and a valid `js-trace-tenant` cookie exists
- **THEN** the system SHALL read the tenant ID from the cookie and set it in the API client header (`X-Tenant-ID`)
- **THEN** the system SHALL call `POST /api/auth/refresh` to obtain a new access token using the httpOnly refresh token cookie
- **WHEN** refresh succeeds
- **THEN** the system SHALL fetch the user profile (`GET /api/auth/me`) and transition to `authenticated` state
- **THEN** the user SHALL remain on their current page without being redirected to login

#### Scenario: Session is cleared after page reload when no cookie exists
- **WHEN** the user reloads the page and no `js-trace-tenant` cookie exists
- **THEN** the system SHALL immediately set session status to `unauthenticated` and redirect to login

#### Scenario: Session is cleared when refresh fails despite cookie being present
- **WHEN** the tenant cookie exists but the refresh token is expired or revoked
- **THEN** the system SHALL call `POST /api/auth/refresh` which returns an error
- **THEN** the system SHALL delete the `js-trace-tenant` cookie, clear session, and redirect to login

### Requirement: Tenant cookie helper is encapsulated in a utility module
The system SHALL expose a dedicated utility module (`src/shared/utils/tenantCookie.ts`) with three functions: `setTenantCookie(id: string)`, `getTenantCookie(): string | null`, `clearTenantCookie()`.

#### Scenario: Helper correctly sets the cookie
- **WHEN** `setTenantCookie("acme")` is called
- **THEN** `document.cookie` SHALL contain `js-trace-tenant=acme`

#### Scenario: Helper correctly reads the cookie
- **WHEN** `js-trace-tenant=acme` is present in `document.cookie`
- **THEN** `getTenantCookie()` SHALL return `"acme"`

#### Scenario: Helper returns null when cookie is absent
- **WHEN** `js-trace-tenant` is not present in `document.cookie`
- **THEN** `getTenantCookie()` SHALL return `null`
