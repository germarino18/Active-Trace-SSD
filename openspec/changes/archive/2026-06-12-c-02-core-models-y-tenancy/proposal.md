## Why

C-01 dejó la estructura vacía: los directorios `models/`, `schemas/`, `repositories/`, `services/` están creados pero no tienen una línea de código. Sin modelos de datos, sin repositorio base y sin aislamiento multi-tenant, ningún change posterior (C-03 auth, C-04 RBAC, C-05 audit, C-06 estructura académica) puede implementar lógica de negocio real. Este change construye la **capa de datos fundacional**: el modelo `Tenant`, los mixins compartidos, el repositorio genérico con scope de tenant, la resolución de tenancy, el cifrado AES-256 para PII, la jerarquía de excepciones y la primera migración de base de datos.

## What Changes

- **`models/tenant.py`**: modelo `Tenant` con UUID como PK, `slug` único por tenant, settings en JSONB, soft delete y timestamps auditables.
- **`models/mixins.py`**: `BaseMixin` (UUID PK + timestamps), `TenantMixin` (FK → tenant), `SoftDeleteMixin` (deleted_at), `AuditMixin` (created_by_id / updated_by_id → User, nullable hasta C-03).
- **`models/base.py`**: `DeclarativeBase` de SQLAlchemy 2.0 con el esquema default y metadatos compartidos.
- **`repositories/base.py`**: `BaseRepository[T]` genérico con CRUD completo, **filtro automático por tenant_id**, soft-delete aware, y operaciones de administración (hard delete restringido).
- **`core/tenancy.py`**: `TenantContext` via `contextvars` para propagar el tenant_id en la cadena de request, y un dependencia FastAPI `get_tenant_id()` que resuelve desde un header/session (placeholder hasta C-03).
- **`core/security.py`**: utilidades AES-256-GCM para cifrar/descifrar PII (CBU, DNI, secretos) usando la biblioteca `cryptography`.
- **`core/exceptions.py`**: jerarquía completa: `AppException` → `NotFoundException`, `ForbiddenException`, `TenantMismatchException`, `ValidationException`, con handlers FastAPI que producen respuestas HTTP estandarizadas.
- **Migración Alembic 001**: creación de la tabla `tenant` con constraints de unicidad, check de slug e índices.
- **Tests**: suite completa con PostgreSQL real (sin mocks) cubriendo CRUD de tenant, aislamiento entre tenants, soft delete, encriptación AES-256 round-trip y operaciones del repositorio base.

No hay cambios BREAKING: C-02 extiende el esqueleto de C-01 con datos reales, no modifica nada existente.

## Capabilities

### New Capabilities

- `tenant-model`: modelo Tenant con UUID, slug único, JSONB para settings, timestamps auditables, soft delete y todas las constraints a nivel base de datos.
- `core-mixins`: mixins reutilizables BaseMixin, TenantMixin, SoftDeleteMixin y AuditMixin que toda entidad del dominio usará.
- `repository-base`: repositorio genérico `BaseRepository[T]` con CRUD async, filtro automático de tenant, soft-delete aware y método `hard_delete` restringido a admin.
- `tenant-resolution`: contexto de tenancy via `contextvars`, dependencia FastAPI `get_tenant_id()`, resolución desde header/session con fallback controlado.
- `aes-encryption`: cifrado/descifrado AES-256-GCM usando `cryptography.hazmat`, con derivación de clave desde `ENCRYPTION_KEY` environment variable.
- `exception-handling`: jerarquía de excepciones de dominio y handlers FastAPI que devuelven respuestas JSON consistentes con código, mensaje y trace ID.
- `database-migration-001`: migración Alembic que crea la tabla `tenant` con índices, constraints de unicidad y check de slug.

### Modified Capabilities

<!-- Ninguna: C-02 define las primeras capacidades del dominio; no hay specs previos que modificar. -->

## Impact

- **Nuevos módulos**: `backend/app/models/tenant.py`, `backend/app/models/mixins.py`, `backend/app/models/base.py`, `backend/app/repositories/base.py`, `backend/app/core/tenancy.py`, `backend/app/core/security.py`, `backend/app/core/exceptions.py`.
- **Migración nueva**: `backend/alembic/versions/001_create_tenant_table.py`.
- **Tests nuevos**: `backend/tests/test_tenant_crud.py`, `backend/tests/test_tenant_isolation.py`, `backend/tests/test_soft_delete.py`, `backend/tests/test_encryption.py`, `backend/tests/test_repository_base.py`.
- **Dependencia nueva**: `cryptography` en `pyproject.toml`.
- **Habilita**: C-03 (auth con JWT), C-04 (RBAC), C-05 (audit log), C-06 (estructura académica). Sin este change ningún modelo de negocio puede existir con tenancy.
- **Governance**: CRÍTICO — multi-tenancy y core-models son la raíz de seguridad del sistema. Cifrado de PII, aislamiento row-level y soft delete son reglas duras no negociables.
