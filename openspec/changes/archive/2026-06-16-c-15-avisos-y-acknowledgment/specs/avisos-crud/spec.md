## ADDED Requirements

### Requirement: Coordinator/Admin can create an aviso
The system SHALL allow users with `avisos:publicar` permission to create an aviso with the following fields: alcance (GLOBAL | POR_MATERIA | POR_COHORTE | POR_ROL), materia_id (nullable), cohorte_id (nullable), rol_destino (nullable string for POR_ROL), severidad (INFO | ADVERTENCIA | CRITICO), titulo, cuerpo, inicio_en, fin_en, orden (integer), activo (boolean), requiere_ack (boolean).

#### Scenario: Create aviso successfully
- **WHEN** a COORDINADOR sends POST /api/v1/avisos with valid aviso data
- **THEN** the system returns 201 with the created aviso as AvisoRead schema

#### Scenario: Create aviso without publicar permission
- **WHEN** an ALUMNO sends POST /api/v1/avisos
- **THEN** the system returns 403 Forbidden

#### Scenario: Create aviso with invalid alcance
- **WHEN** a COORDINADOR sends POST /api/v1/avisos with alcance="Invalid"
- **THEN** the system returns 422 Validation Error

#### Scenario: Create aviso without required fields
- **WHEN** a COORDINADOR sends POST /api/v1/avisos without titulo
- **THEN** the system returns 422 Validation Error

### Requirement: Coordinator/Admin can update an aviso
The system SHALL allow users with `avisos:publicar` permission to partially update an aviso's fields.

#### Scenario: Update aviso fields successfully
- **WHEN** a COORDINADOR sends PATCH /api/v1/avisos/{id} with valid update data
- **THEN** the system returns 200 with the updated aviso

#### Scenario: Update non-existent aviso
- **WHEN** a COORDINADOR sends PATCH /api/v1/avisos/{non_existent_id}
- **THEN** the system returns 404 Not Found

#### Scenario: Update aviso from different tenant
- **WHEN** a COORDINADOR from tenant A sends PATCH /api/v1/avisos/{id_from_tenant_B}
- **THEN** the system returns 404 Not Found (tenant scoping)

### Requirement: Coordinator/Admin can soft-delete an aviso
The system SHALL soft-delete an aviso (set deleted_at) when a user with `avisos:publicar` requests deletion.

#### Scenario: Soft-delete aviso
- **WHEN** a COORDINADOR sends DELETE /api/v1/avisos/{id}
- **THEN** the system returns 204 No Content and the aviso's deleted_at is set

#### Scenario: Cannot delete without permission
- **WHEN** an ALUMNO sends DELETE /api/v1/avisos/{id}
- **THEN** the system returns 403 Forbidden

### Requirement: Coordinator/Admin can get a single aviso
The system SHALL return a single aviso by ID for users with `avisos:publicar` permission.

#### Scenario: Get aviso by ID
- **WHEN** a COORDINADOR sends GET /api/v1/avisos/{id}
- **THEN** the system returns 200 with the aviso data

#### Scenario: Get non-existent aviso
- **WHEN** a COORDINADOR sends GET /api/v1/avisos/{non_existent_id}
- **THEN** the system returns 404 Not Found

### Requirement: Coordinator/Admin can list all avisos
The system SHALL return a paginated list of avisos (including inactive and expired) for users with `avisos:publicar` permission, ordered by orden ascending then created_at descending.

#### Scenario: List avisos with pagination
- **WHEN** a COORDINADOR sends GET /api/v1/avisos?skip=0&limit=20
- **THEN** the system returns 200 with a list of avisos and pagination metadata

#### Scenario: List avisos without permission
- **WHEN** an ALUMNO sends GET /api/v1/avisos
- **THEN** the system returns 403 Forbidden
