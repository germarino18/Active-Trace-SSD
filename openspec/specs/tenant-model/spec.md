## ADDED Requirements

### Requirement: Tenant model structure
The system SHALL define a `Tenant` SQLAlchemy model with the following columns:
- `id`: UUID primary key, server default `gen_random_uuid()`
- `name`: VARCHAR(255), NOT NULL
- `slug`: VARCHAR(100), NOT NULL, unique among active records
- `settings`: JSONB, NOT NULL, default `'{}'`
- `is_active`: BOOLEAN, NOT NULL, default `TRUE`
- `created_at`: TIMESTAMPTZ, NOT NULL, server default `NOW()`
- `updated_at`: TIMESTAMPTZ, NOT NULL, server default `NOW()`, auto-updates on modification
- `deleted_at`: TIMESTAMPTZ, nullable
- `created_by_id`: UUID, nullable (reserved for FK → User in C-03)
- `updated_by_id`: UUID, nullable (reserved for FK → User in C-03)

#### Scenario: Create tenant with all fields
- **WHEN** creating a new Tenant with valid name "Test University" and slug "test-university"
- **THEN** a UUID id is auto-generated, created_at and updated_at are set to current timestamp, and all fields persist correctly

#### Scenario: Slug uniqueness among active records
- **WHEN** creating two tenants with the same slug "my-uni" where the first is NOT soft-deleted
- **THEN** the second creation raises an integrity error because the partial unique index `ix_tenant_slug` enforces uniqueness where `deleted_at IS NULL`

#### Scenario: Slug reuse after soft delete
- **WHEN** creating a tenant with slug "old-uni", soft-deleting it, then creating another tenant with slug "old-uni"
- **THEN** the second creation succeeds because the partial unique index allows duplicate slugs among deleted records

### Requirement: Tenant settings as JSONB
The system SHALL store tenant configuration as a JSONB column with free-form key-value structure, validated at application level (not DB level).

#### Scenario: Store and retrieve arbitrary settings
- **WHEN** saving a Tenant with `settings = {"moodle_url": "https://moodle.example.com", "max_students": 500}`
- **THEN** the settings are persisted as JSONB and retrieved with the same structure

### Requirement: Soft delete on Tenant
The Tenant model SHALL support soft delete by setting `deleted_at` to the current timestamp, excluding it from default queries.

#### Scenario: Soft delete excludes from default query
- **WHEN** soft-deleting a tenant and then querying all tenants without explicit deleted inclusion
- **THEN** the soft-deleted tenant is NOT present in the results

#### Scenario: Include deleted tenant explicitly
- **WHEN** querying tenants with explicit include_deleted flag
- **THEN** soft-deleted tenants are included in the results, with their `deleted_at` timestamp populated
