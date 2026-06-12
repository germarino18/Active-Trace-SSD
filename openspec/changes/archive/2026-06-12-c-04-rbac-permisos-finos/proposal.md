## Why

activia-trace has multi-tenant row-level auth and JWT-based identity (C-03), but no authorization layer beyond raw role strings in the JWT. Every protected action currently needs ad-hoc checks. This change implements fine-grained RBAC with `modulo:accion` permissions, a managed role/permission catalog in the database, and a declarative `require_permission` guard — enabling endpoint-level authorization that is fail-closed, tenant-scoped, and administrable without code changes.

## What Changes

- **New tables**: `rol` (role catalog), `permiso` (permission catalog `modulo:accion`), `rol_permiso` (many-to-many matrix) — all tenant-aware, administrable via API.
- **Seed data**: 7 domain roles (ALUMNO, TUTOR, PROFESOR, COORDINADOR, NEXO, ADMIN, FINANZAS) with the permission matrix from `03_actores_y_roles.md` §3.3.
- **`require_permission(permiso)` dependency**: FastAPI guard that resolves effective permissions from the user's active role assignments (union of roles, tenant-scoped, checked against vigencia if `Asignacion` table exists). Without explicit permission → 403.
- **`(propio)` modifier support**: server-side resolution for permissions scoped to the user's own data (e.g., PROFESOR sees only their own `calificaciones:importar`).
- **CRUD admin endpoints**: `/api/admin/roles`, `/api/admin/permisos` for catalog management (ADMIN only, requires `estructura:gestionar` or equivalent admin permission).
- **Migration 003**: Alembic migration creating `rol`, `permiso`, `rol_permiso` tables with seed data.
- **Tests**: user without permission → 403, role union, `(propio)` scope, catalog CRUD.

## Capabilities

### New Capabilities
- `rbac-catalog`: Role and permission entity model, admin-manageable catalog with CRUD endpoints
- `permission-resolver`: Server-side resolution of effective permissions from role assignments (union, tenant-scoped, potentially time-bound)
- `require-permission-guard`: FastAPI dependency that enforces `modulo:accion` on endpoints, returning 403 on failure
- `own-data-scope`: Server-side enforcement of the `(propio)` modifier, filtering data access to the current user

### Modified Capabilities
- *(none — first permission-related change)*

## Impact

- **New models**: `Rol`, `Permiso`, `RolPermiso` in `backend/app/models/`
- **New schemas**: `RolCreate/Update/Response`, `PermisoCreate/Update/Response` in `backend/app/schemas/`
- **New repositories**: `RolRepository`, `PermisoRepository` in `backend/app/repositories/`
- **New service**: `PermissionService` (resolver) in `backend/app/services/`
- **Modified**: `backend/app/core/dependencies.py` — add `require_permission` dependency
- **Modified**: `backend/app/core/permissions.py` — was a stub, will hold permission constants/enums and the resolver logic
- **New router**: `/api/v1/routers/admin.py` — admin-only CRUD for roles and permissions
- **Migration 003**: new migration file in `backend/alembic/versions/`
- **Governance**: CRITICO — propose first, no code without approval
