## ADDED Requirements

### Requirement: Migration 001 creates tenant table
The system SHALL provide an Alembic migration that creates the `tenant` table with all columns, constraints, and indexes as defined in the Tenant model.

#### Scenario: Migration creates tenant table with all columns
- **WHEN** running `alembic upgrade head`
- **THEN** the `tenant` table exists with columns: id (UUID PK), name (VARCHAR), slug (VARCHAR), settings (JSONB), is_active (BOOLEAN), created_at (TIMESTAMPTZ), updated_at (TIMESTAMPTZ), deleted_at (TIMESTAMPTZ nullable), created_by_id (UUID nullable), updated_by_id (UUID nullable)

#### Scenario: Migration creates partial unique index on active slugs
- **WHEN** inspecting the `tenant` table indexes after migration
- **THEN** there is a partial unique index `ix_tenant_slug` on `slug` WHERE `deleted_at IS NULL`

#### Scenario: Migration creates composite index for slug + deleted_at
- **WHEN** inspecting the `tenant` table indexes after migration
- **THEN** there is an index `ix_tenant_slug_deleted` on `(slug, deleted_at)` for querying deleted records by slug

#### Scenario: Rollback drops tenant table
- **WHEN** running `alembic downgrade -1`
- **THEN** the `tenant` table is dropped

### Requirement: Migration is idempotent
The migration SHALL be written such that it can be run multiple times without error (using `CREATE TABLE IF NOT EXISTS` or Alembic's auto-detection of existing objects).

#### Scenario: Migration upgrade is idempotent
- **WHEN** running `alembic upgrade head` twice
- **THEN** the second run reports "no changes detected" and succeeds without error
