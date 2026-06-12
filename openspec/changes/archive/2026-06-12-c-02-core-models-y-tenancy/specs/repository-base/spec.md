## ADDED Requirements

### Requirement: Generic BaseRepository with CRUD operations
The system SHALL provide a `BaseRepository[T]` generic class that implements standard CRUD operations for any SQLAlchemy model.

#### Scenario: Create and persist a new record
- **WHEN** calling `repository.create(data)` with valid Pydantic-like data
- **THEN** the record is inserted into the database, a UUID is generated, and the created instance is returned

#### Scenario: Find record by UUID
- **WHEN** calling `repository.find_by_id(uuid)` with an existing record's UUID
- **THEN** the record is returned; when called with a non-existent UUID, None is returned

#### Scenario: Find all records with pagination
- **WHEN** calling `repository.find_all()` with optional skip/limit parameters
- **THEN** a list of records is returned, respecting pagination limits; an empty list if no records exist

#### Scenario: Find records by arbitrary filters
- **WHEN** calling `repository.find_by(**filters)` with column-value pairs
- **THEN** only matching records are returned

#### Scenario: Update an existing record
- **WHEN** calling `repository.update(uuid, data)` with a valid UUID and update data
- **THEN** the record is updated with the new values and the updated instance is returned

#### Scenario: Update raises NotFoundException for missing record
- **WHEN** calling `repository.update(non_existent_uuid, data)`
- **THEN** a NotFoundException is raised

### Requirement: Automatic tenant scoping on ALL queries
The BaseRepository SHALL automatically apply a `WHERE tenant_id = :tenant_id` filter to ALL queries when a tenant_id is available.

#### Scenario: Tenant A cannot access Tenant B records
- **WHEN** creating two records under different tenants and querying through repository scoped to Tenant A
- **THEN** only Tenant A's records are returned; Tenant B's records are invisible

#### Scenario: find_by_id respects tenant scope
- **WHEN** calling `find_by_id(uuid)` where the record exists but belongs to a different tenant
- **THEN** None is returned (the record is invisible to this tenant scope)

#### Scenario: find_all respects tenant scope
- **WHEN** calling `find_all()` on a repository scoped to Tenant A when records exist for both Tenant A and Tenant B
- **THEN** only Tenant A's records are returned

### Requirement: Soft-delete awareness
The BaseRepository SHALL automatically exclude soft-deleted records from default queries, and provide a method to include them.

#### Scenario: Default query excludes soft-deleted records
- **WHEN** calling `repository.find_all()` after soft-deleting a record
- **THEN** the soft-deleted record is NOT present in results

#### Scenario: include_deleted() returns all records including deleted
- **WHEN** calling `repository.include_deleted().find_all()` after soft-deleting a record
- **THEN** all records (including deleted) are returned

#### Scenario: soft_delete sets deleted_at
- **WHEN** calling `repository.soft_delete(uuid)` on an existing record
- **THEN** the record's `deleted_at` is set to current timestamp and the record is excluded from subsequent default queries

### Requirement: Hard delete restricted without tenant scope
The BaseRepository SHALL provide a `hard_delete()` method that permanently removes a record. This method MUST require explicit opt-in and SHOULD be restricted to administrative operations.

#### Scenario: Hard delete removes permanently
- **WHEN** calling `repository.hard_delete(uuid)` on an existing record
- **THEN** the record is permanently removed and subsequent `find_by_id(uuid)` returns None
