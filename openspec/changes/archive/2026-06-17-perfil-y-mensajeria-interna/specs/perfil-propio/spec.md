## ADDED Requirements

### Requirement: GET perfil propio returns current user profile

The system SHALL expose `GET /api/v1/perfil` that returns the authenticated user's profile data from the `usuario` table, linked via the JWT identity (`user_id` → `usuario.user_id`). The response SHALL include: `id`, `nombre`, `apellidos`, `email`, `dni`, `cuil`, `cbu`, `alias_cbu`, `banco`, `regional`, `legajo`, `legajo_profesional`, `facturador`, `estado`. PII fields (dni, cuil, cbu, alias_cbu) SHALL be decrypted for the owner.

#### Scenario: Own profile returned successfully
- **WHEN** an authenticated user calls GET `/api/v1/perfil`
- **THEN** the response is 200 with the user's profile data, PII fields decrypted

#### Scenario: Profile not found returns 404
- **WHEN** an authenticated user calls GET `/api/v1/perfil` but has no `usuario` row linked
- **THEN** the response is 404 Not Found

#### Scenario: Tenant isolation
- **WHEN** two users from different tenants call GET `/api/v1/perfil`
- **THEN** each receives only their own profile, scoped to their tenant

### Requirement: PATCH perfil propio edits editable fields

The system SHALL expose `PATCH /api/v1/perfil` that accepts a partial update of the authenticated user's profile. Editable fields: `nombre`, `apellidos`, `dni`, `banco`, `cbu`, `alias_cbu`, `regional`, `legajo_profesional`, `facturador`. The field `cuil` SHALL be rejected if included in the request body. PII fields SHALL be encrypted before storage.

#### Scenario: PATCH updates editable fields
- **WHEN** an authenticated user calls PATCH `/api/v1/perfil` with `{"nombre": "Nuevo Nombre", "banco": "Nación"}`
- **THEN** the response is 200 with the updated profile; nombre and banco are changed

#### Scenario: PATCH with CUIL returns 422
- **WHEN** an authenticated user calls PATCH `/api/v1/perfil` with `{"cuil": "20-12345678-9"}`
- **THEN** the response is 422 Unprocessable Entity indicating cuil is not editable

#### Scenario: PATCH with no valid fields returns 422
- **WHEN** an authenticated user calls PATCH `/api/v1/perfil` with an empty body or only read-only fields
- **THEN** the response is 422 Unprocessable Entity

#### Scenario: PATCH scoped to own user
- **WHEN** user A calls PATCH `/api/v1/perfil`
- **THEN** only user A's profile is updated, regardless of any `id` in the body (ignored)

### Requirement: All authenticated users can access perfil

The system SHALL allow any authenticated user (any role) to access GET and PATCH `/api/v1/perfil`. No specific permission is required beyond a valid JWT.

#### Scenario: Any authenticated role can access
- **WHEN** a user with role ALUMNO, TUTOR, PROFESOR, COORDINADOR, NEXO, ADMIN, or FINANZAS calls GET `/api/v1/perfil`
- **THEN** the response is 200
