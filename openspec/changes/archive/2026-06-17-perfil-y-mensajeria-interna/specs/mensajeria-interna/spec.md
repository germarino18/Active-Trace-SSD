## ADDED Requirements

### Requirement: GET hilos returns inbox threads

The system SHALL expose `GET /api/v1/inbox/hilos` that returns the authenticated user's conversation threads (hilos), sorted by most recent message descending. Each hilo SHALL include: `id`, `remitente_id`, `remitente_nombre`, `asunto`, `ultimo_mensaje` (preview), `ultima_fecha`, `no_leido` (boolean). Only hilos where the user is either remitente or destinatario SHALL be returned.

#### Scenario: Hilos returned sorted by recency
- **WHEN** an authenticated user calls GET `/api/v1/inbox/hilos`
- **THEN** the response is 200 with an array of hilos sorted by `ultima_fecha` descending

#### Scenario: Hilos are tenant-scoped
- **WHEN** users from different tenants have hilos
- **THEN** each user only sees hilos within their own tenant

#### Scenario: Empty inbox returns empty array
- **WHEN** an authenticated user with no messages calls GET `/api/v1/inbox/hilos`
- **THEN** the response is 200 with an empty array

### Requirement: GET hilo/{id} returns messages in a thread

The system SHALL expose `GET /api/v1/inbox/hilos/{id}` that returns all messages in a specific hilo, sorted chronologically. Each message SHALL include: `id`, `remitente_id`, `remitente_nombre`, `contenido`, `fecha_hora`. Messages SHALL be tenant-scoped and only accessible if the user is participant in the hilo.

#### Scenario: Hilo messages returned chronologically
- **WHEN** an authenticated user calls GET `/api/v1/inbox/hilos/{id}` for a hilo they participate in
- **THEN** the response is 200 with an array of messages sorted by `fecha_hora` ascending

#### Scenario: Hilo from another tenant returns 404
- **WHEN** an authenticated user calls GET `/api/v1/inbox/hilos/{id}` for a hilo from a different tenant
- **THEN** the response is 404 Not Found

#### Scenario: Non-participant gets 404
- **WHEN** an authenticated user calls GET `/api/v1/inbox/hilos/{id}` for a hilo where they are not a participant
- **THEN** the response is 404 Not Found

#### Scenario: Non-existent hilo returns 404
- **WHEN** an authenticated user calls GET `/api/v1/inbox/hilos/{id}` with a non-existent UUID
- **THEN** the response is 404 Not Found

### Requirement: POST responder in a hilo

The system SHALL expose `POST /api/v1/inbox/hilos/{id}/responder` that adds a new message to an existing hilo. The request body SHALL include `contenido` (text, required, max 2000 chars). The response SHALL return the created message. Only hilo participants can reply. A reply SHALL automatically mark the hilo as "no leído" for the other participant.

#### Scenario: Reply succeeds
- **WHEN** an authenticated user calls POST `/api/v1/inbox/hilos/{id}/responder` with `{"contenido": "Gracias por la info"}`
- **THEN** the response is 201 with the created message; the other participant's `no_leido` flag is set to true

#### Scenario: Reply by non-participant returns 404
- **WHEN** an authenticated user who is not a participant calls POST `/api/v1/inbox/hilos/{id}/responder`
- **THEN** the response is 404 Not Found

#### Scenario: Reply with empty content returns 422
- **WHEN** an authenticated user calls POST `/api/v1/inbox/hilos/{id}/responder` with `{"contenido": ""}`
- **THEN** the response is 422 Unprocessable Entity

#### Scenario: Reply with content exceeding max length returns 422
- **WHEN** an authenticated user calls POST `/api/v1/inbox/hilos/{id}/responder` with content exceeding 2000 characters
- **THEN** the response is 422 Unprocessable Entity

### Requirement: Permission inbox:acceder

The system SHALL define a new permission `inbox:acceder` that gates access to all `/api/v1/inbox/*` endpoints. This permission SHALL be assigned by default to all authenticated user roles (ALUMNO, TUTOR, PROFESOR, COORDINADOR, NEXO, ADMIN, FINANZAS).

#### Scenario: Authenticated user with inbox:acceder can access
- **WHEN** an authenticated user with any role calls GET `/api/v1/inbox/hilos`
- **THEN** the response is 200

#### Scenario: Unauthenticated request returns 401
- **WHEN** an unauthenticated request calls GET `/api/v1/inbox/hilos`
- **THEN** the response is 401 Unauthorized
