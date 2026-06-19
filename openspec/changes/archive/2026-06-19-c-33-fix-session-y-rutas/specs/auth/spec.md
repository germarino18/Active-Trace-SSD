## MODIFIED Requirements

### Requirement: Tokens refresh transparently
The system SHALL automatically refresh the access token when it expires, without user intervention. Additionally, the system SHALL restore the authenticated session on page reload by reading the tenant ID from the `js-trace-tenant` session cookie before attempting token refresh.

#### Scenario: Transparent refresh on 401
- **WHEN** the access token expires and the Axios interceptor receives a 401 response
- **THEN** the system calls POST `/api/auth/refresh` using the httpOnly cookie
- **WHEN** refresh succeeds
- **THEN** the system retries the original request with the new access token
- **WHEN** refresh fails (expired or revoked refresh token)
- **THEN** the system clears the session, deletes the `js-trace-tenant` cookie, and redirects to login

#### Scenario: Session restored on mount when tenant cookie exists
- **WHEN** `AuthProvider` mounts and a `js-trace-tenant` cookie is present
- **THEN** the system SHALL read the tenant ID from the cookie and configure the API client with `X-Tenant-ID` header
- **THEN** the system SHALL call `POST /api/auth/refresh`
- **WHEN** refresh succeeds
- **THEN** the system SHALL fetch `GET /api/auth/me` and set session status to `authenticated`
- **WHEN** refresh fails
- **THEN** the system SHALL delete the tenant cookie and set session status to `unauthenticated`

#### Scenario: Session not attempted when no tenant cookie on mount
- **WHEN** `AuthProvider` mounts and no `js-trace-tenant` cookie is present
- **THEN** the system SHALL immediately set session status to `unauthenticated` without calling the refresh endpoint
