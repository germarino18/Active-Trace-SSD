## 1. Foundation — Mixins, Base & Exceptions

- [x] 1.1 Create `models/base.py` with `DeclarativeBase` from SQLAlchemy 2.0, shared metadata, and `mapper_registry`
- [x] 1.2 Create `models/mixins.py` with `BaseMixin` (UUID PK, created_at, updated_at), `TenantMixin` (tenant_id FK), `SoftDeleteMixin` (deleted_at, soft_delete method), and `AuditMixin` (created_by_id, updated_by_id nullable)
- [x] 1.3 Create `models/__init__.py` re-exporting Base, all mixins, and Tenant
- [x] 1.4 Create `core/exceptions.py` with `AppException` base and `NotFoundException`, `ForbiddenException`, `TenantMismatchException`, `ValidationException` subclasses, each with `message`, `code`, and `details`
- [x] 1.5 Register global exception handlers in `app/main.py` that catch `AppException` and return standardized JSON responses with correct HTTP status codes

## 2. Tenant Model

- [x] 2.1 Create `models/tenant.py` with `Tenant` model class inheriting from BaseMixin, TenantMixin (self-referencing), SoftDeleteMixin, and AuditMixin
- [x] 2.2 Add `slug` column with unique constraint, `name`, `settings` (JSONB, default `{}`), and `is_active` (default True)
- [x] 2.3 Add `__table_args__` with partial unique index `ix_tenant_slug` on `slug WHERE deleted_at IS NULL` and composite index `ix_tenant_slug_deleted` on `(slug, deleted_at)`

## 3. Database Migration 001

- [x] 3.1 Generate Alembic migration `001_create_tenant_table` using `alembic revision --autogenerate`
- [x] 3.2 Review and edit the generated migration: ensure partial unique index and composite index are correct, remove any auto-generated FK constraints for created_by_id/updated_by_id (User table doesn't exist yet)
- [x] 3.3 Verify migration is idempotent: run `alembic upgrade head` twice, confirm second run reports no changes
- [x] 3.4 Verify rollback: run `alembic downgrade -1`, confirm tenant table is dropped, then re-apply with `alembic upgrade head`

## 4. AES-256 Security Helpers

- [x] 4.1 Add `cryptography` dependency to `pyproject.toml`
- [x] 4.2 Create `core/security.py` with `get_encryption_key()` that reads `ENCRYPTION_KEY` from settings and validates it's a 64-char hex string
- [x] 4.3 Implement `encrypt_value(plaintext: str, key: bytes) -> str` using AES-256-GCM with random 12-byte nonce, returning base64 encoded `nonce + tag + ciphertext`
- [x] 4.4 Implement `decrypt_value(ciphertext_b64: str, key: bytes) -> str` that decodes base64, extracts nonce/tag/ciphertext, and decrypts with GCM verification

## 5. Tenant Resolution & Context

- [x] 5.1 Create `core/tenancy.py` with `TenantContext` class using `contextvars.ContextVar[uuid.UUID | None]` and static methods `get()`, `set()`, `reset()`
- [x] 5.2 Implement FastAPI middleware `TenantMiddleware` that extracts tenant_id from `X-Tenant-ID` header, sets `TenantContext`, and resets in `finally` block
- [x] 5.3 Create `get_tenant_id()` FastAPI dependency that reads from `TenantContext.get()` first, falls back to `X-Tenant-ID` header, and raises `TenantMismatchException` if neither is available

## 6. Repository Base

- [x] 6.1 Create `repositories/base.py` with generic `BaseRepository[T]` class, constructor receiving `AsyncSession` and optional `tenant_id`
- [x] 6.2 Implement `_apply_tenant_scope(query)` that adds `WHERE tenant_id = :tenant_id` when tenant_id is set
- [x] 6.3 Implement `_apply_soft_delete_filter(query)` that adds `WHERE deleted_at IS NULL` by default
- [x] 6.4 Implement `create(data: dict | BaseModel) -> T` that instantiates the model, adds tenant_id from scope, flushes, and refreshes
- [x] 6.5 Implement `find_by_id(id: UUID) -> T | None` with tenant scope and soft-delete filter
- [x] 6.6 Implement `find_all(*, skip: int = 0, limit: int = 100) -> list[T]` with tenant scope, soft-delete filter, and pagination
- [x] 6.7 Implement `find_by(**filters) -> list[T]` with tenant scope, soft-delete filter, and arbitrary column filters
- [x] 6.8 Implement `update(id: UUID, data: dict | BaseModel) -> T` that raises `NotFoundException` if record doesn't exist
- [x] 6.9 Implement `soft_delete(id: UUID) -> T` that sets `deleted_at` and returns the updated record
- [x] 6.10 Implement `hard_delete(id: UUID) -> None` for permanent removal (admin-only semantic)
- [x] 6.11 Implement `include_deleted() -> Self` context manager/fluent method that disables the soft-delete filter for chained queries

## 7. Tests

- [x] 7.1 Write `tests/test_tenant_crud.py`: test creating, reading, updating, and soft-deleting a Tenant with real PostgreSQL
- [x] 7.2 Write `tests/test_tenant_isolation.py`: test that repository scoped to Tenant A cannot see Tenant B's records, covering find_by_id, find_all, and find_by
- [x] 7.3 Write `tests/test_soft_delete.py`: test that soft-deleted records are excluded by default, included with `include_deleted()`, and restorable by setting deleted_at to None
- [x] 7.4 Write `tests/test_encryption.py`: test AES-256 round-trip, different ciphertexts for same plaintext, decrypt with wrong key raises exception, tampered ciphertext raises exception, and invalid ENCRYPTION_KEY raises ValueError
- [x] 7.5 Write `tests/test_repository_base.py`: test all CRUD operations with tenant scope, pagination, filtering, NotFoundException on update of missing record, and hard delete
- [x] 7.6 Write `tests/conftest.py` fixtures: `db_session` (transactional rollback), `test_tenant` (persisted Tenant), `another_tenant` (second Tenant for isolation tests), and `repository` (BaseRepository bound to test_tenant)

## 8. Wiring & Integration

- [x] 8.1 Register `TenantMiddleware` in the FastAPI app lifespan/middleware stack in `app/main.py`
- [x] 8.2 Wire exception handlers into the FastAPI app in `app/main.py`
- [x] 8.3 Add `ENCRYPTION_KEY` to `.env.example` with a placeholder comment indicating 64-char hex format
- [x] 8.4 Verify all tests pass: `pytest -v --asyncio-mode=auto` with all 43 tests green — ✅ PostgreSQL + fixes applied
- [x] 8.5 Run linting/type checking: `ruff check .` and `mypy backend/app/` (if configured) — zero errors
