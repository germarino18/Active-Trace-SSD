## ADDED Requirements

### Requirement: HTTP client is a centralized Axios instance
The system SHALL provide a single Axios instance configured with base URL, default headers, request interceptor, and response interceptor.

#### Scenario: Default configuration
- **WHEN** the Axios instance is created
- **THEN** it SHALL have `baseURL` set to an empty string (Vite proxy handles `/api/*`)
- **THEN** it SHALL have a default timeout of 30 seconds

### Requirement: Request interceptor attaches Authorization header
The system SHALL attach the current access token to every outgoing request.

#### Scenario: Attach access token
- **WHEN** a request is made
- **THEN** the interceptor reads the access token from AuthContext
- **WHEN** a token exists
- **THEN** the interceptor sets `Authorization: Bearer <token>`

### Requirement: Response interceptor handles 401 with transparent refresh
The system SHALL intercept 401 responses and attempt a single transparent token refresh before retrying.

#### Scenario: Single refresh on 401
- **WHEN** any request receives a 401 response
- **THEN** the interceptor attempts POST `/api/auth/refresh`
- **WHEN** refresh succeeds (new tokens returned)
- **THEN** the interceptor updates the access token in AuthContext and retries the original request with the new token
- **WHEN** refresh also fails (401 or other error)
- **THEN** the interceptor clears the session, calls the logout handler, and rejects with the original error

#### Scenario: Concurrent 401s use a single refresh
- **WHEN** multiple requests receive a 401 simultaneously
- **THEN** only one refresh call is made
- **THEN** all queued requests retry with the new token once the refresh succeeds

### Requirement: HTTP client exports typed request functions
The system SHALL export typed wrapper functions for common HTTP methods.

#### Scenario: Typed wrappers
- **WHEN** a feature service calls `api.get<T>('/path')` or `api.post<T>('/path', body)`
- **THEN** the response is typed as `AxiosResponse<T>`
