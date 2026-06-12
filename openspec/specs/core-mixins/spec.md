## ADDED Requirements

### Requirement: BaseMixin provides UUID PK and timestamps
The system SHALL provide a `BaseMixin` that adds `id` (UUID PK), `created_at`, and `updated_at` columns to any model that inherits from it.

#### Scenario: Model with BaseMixin has auto-generated UUID
- **WHEN** creating a model instance that uses BaseMixin without passing an `id`
- **THEN** a UUID v4 is auto-generated and assigned as the primary key

#### Scenario: Model with BaseMixin has automatic timestamps
- **WHEN** creating a new model instance with BaseMixin
- **THEN** `created_at` and `updated_at` are set to the current UTC timestamp; on update, `updated_at` refreshes to current UTC timestamp

### Requirement: TenantMixin adds tenant_id FK
The system SHALL provide a `TenantMixin` that adds a `tenant_id` column as a non-nullable UUID foreign key referencing `tenant.id`.

#### Scenario: Model with TenantMixin requires tenant_id
- **WHEN** creating a model instance that uses TenantMixin without providing a `tenant_id`
- **THEN** an integrity error is raised because tenant_id is NOT NULL

#### Scenario: Model with TenantMixin correctly references tenant
- **WHEN** creating a model instance that uses TenantMixin with a valid existing tenant UUID
- **THEN** the relationship resolves correctly and the tenant's attributes are accessible via the relationship

### Requirement: SoftDeleteMixin adds deleted_at
The system SHALL provide a `SoftDeleteMixin` that adds a nullable `deleted_at` TIMESTAMPTZ column and provides a `soft_delete()` method that sets it to the current timestamp.

#### Scenario: Soft delete sets deleted_at
- **WHEN** calling `soft_delete()` on a model instance that uses SoftDeleteMixin
- **THEN** `deleted_at` is set to the current UTC timestamp, and the record is marked as deleted

#### Scenario: Restore after soft delete
- **WHEN** setting `deleted_at = None` on a soft-deleted instance and committing
- **THEN** the record is restored (no longer considered deleted)

### Requirement: AuditMixin adds created_by and updated_by
The system SHALL provide an `AuditMixin` that adds nullable `created_by_id` and `updated_by_id` UUID columns (reserved for future FK to User model).

#### Scenario: Audit fields are nullable
- **WHEN** creating a model instance with AuditMixin without providing `created_by_id` or `updated_by_id`
- **THEN** both fields default to NULL without raising an error

### Requirement: Mixins compose cleanly via single inheritance
The system SHALL provide a `DeclarativeBase` that includes all applicable mixins, so that concrete models can use single inheritance rather than multiple mixin composition.

#### Scenario: Model inheriting from Base gets all mixin columns
- **WHEN** defining a model that inherits from the project's DeclarativeBase
- **THEN** it automatically includes `id`, `created_at`, `updated_at`, `tenant_id`, and `deleted_at` columns
