## 1. Foundation — Models, Schemas, and Migration

- [x] 1.1 Create `Rol` model in `app/models/rol.py`: inherits `BaseMixin`, `TenantMixin`, `SoftDeleteMixin`, `AuditMixin`. Columns: `codigo` (VARCHAR 50, unique per tenant), `nombre` (VARCHAR 100), `descripcion` (TEXT nullable). Partial unique index on `(tenant_id, codigo) WHERE deleted_at IS NULL`.
- [x] 1.2 Create `Permiso` model in `app/models/permiso.py`: inherits `BaseMixin`, `TenantMixin`, `SoftDeleteMixin`, `AuditMixin`. Columns: `codigo` (VARCHAR 100, unique per tenant) — format `modulo:accion`, `nombre` (VARCHAR 255), `descripcion` (TEXT nullable), `modulo` (VARCHAR 50). Partial unique index on `(tenant_id, codigo) WHERE deleted_at IS NULL`.
- [x] 1.3 Create `RolPermiso` model in `app/models/rol_permiso.py`: inherits `BaseMixin`, `TenantMixin`. Columns: `rol_id` (UUID FK → rol.id), `permiso_id` (UUID FK → permiso.id), `es_propio` (BOOLEAN default FALSE). Unique constraint on `(tenant_id, rol_id, permiso_id)`.
- [x] 1.4 Create Pydantic schemas in `app/schemas/permissions.py`: `RolCreate`, `RolUpdate`, `RolResponse`, `PermisoCreate`, `PermisoUpdate`, `PermisoResponse`, `RolPermisoCreate` — all with `extra='forbid'`.
- [x] 1.5 Generate Alembic migration 003 creating tables `rol`, `permiso`, `rol_permiso` (rename migration file properly).
- [x] 1.6 Add seed data to migration 003: insert 7 roles (ALUMNO, TUTOR, PROFESOR, COORDINADOR, NEXO, ADMIN, FINANZAS) and all `permiso` rows from the matrix in `03_actores_y_roles.md` §3.3.
- [x] 1.7 Add seed `rol_permiso` data to migration 003: insert all role-permission assignments based on the matrix, with `es_propio=TRUE` where `(propio)` is marked. NEXO gets zero permissions (pending PA-25).
- [x] 1.8 Register new models in `app/models/__init__.py`.

## 2. Repositories

- [x] 2.1 Create `RolRepository` in `app/repositories/rol_repository.py`: inherits `BaseRepository[Rol]`. Add `find_by_codigo(tenant_id, codigo)` helper.
- [x] 2.2 Create `PermisoRepository` in `app/repositories/permiso_repository.py`: inherits `BaseRepository[Permiso]`. Add `find_by_codigo(tenant_id, codigo)` and `find_by_modulo(tenant_id, modulo)` helpers.
- [x] 2.3 Create `RolPermisoRepository` in `app/repositories/rol_permiso_repository.py`: inherits `BaseRepository[RolPermiso]`. Add `find_permisos_for_roles(tenant_id, role_codes: list[str])` — single JOIN query returning all effective permissions for a set of role codes.

## 3. Permission Service and Constants

- [x] 3.1 Define permission string constants in `app/core/permissions.py` as a `Perm` class with attributes for every permission from the matrix (e.g., `CALIFICACIONES_IMPORTAR = "calificaciones:importar"`, `ATRASADOS_VER = "atrasados:ver"`, `COMUNICACION_ENVIAR = "comunicacion:enviar"`, `COMUNICACION_APROBAR = "comunicacion:aprobar"`, `EQUIPOS_ASIGNAR = "equipos:asignar"`, `LIQUIDACIONES_CERRAR = "liquidaciones:cerrar"`, `AUDITORIA_VER = "auditoria:ver"`, `IMPERSONACION_USAR = "impersonacion:usar"`, `ESTRUCTURA_GESTIONAR = "estructura:gestionar"`, `USUARIOS_GESTIONAR = "usuarios:gestionar"`, `CONFIGURAR_TENANT = "configurar:tenant"`, `AVISOS_PUBLICAR = "avisos:publicar"`, `FACTURAS_GESTIONAR = "facturas:gestionar"`, `GRILLA_OPERAR = "grilla:operar"`, `TAREAS_GESTIONAR = "tareas:gestionar"`, `ENCUENTROS_GESTIONAR = "encuentros:gestionar"`, `GUARDIAS_REGISTRAR = "guardias:registrar"`, etc.).
- [x] 3.2 Create `PermissionResolver` in `app/services/permission_service.py` with:
    - `get_effective_permissions(tenant_id: UUID, role_codes: list[str]) -> set[str]`: fetches all `rol_permiso` entries for the given roles via `RolPermisoRepository`, returns a set of `permiso_codigo` strings.
    - Per-request cache via `contextvars` so multiple `require_permission` calls in the same request hit cache.
    - Method also returns `es_propio` metadata for `(propio)` enforcement.

## 4. Guard Dependency and Endpoint Integration

- [x] 4.1 Implement `require_permission(permiso: str)` dependency in `app/core/dependencies.py`:
    - Accepts a permission string (e.g., `Perm.CALIFICACIONES_IMPORTAR`).
    - Uses `PermissionResolver` to get effective permissions for the current user's roles.
    - If permission not in the effective set → raises `ForbiddenException`.
    - Returns permission metadata (including `es_propio` flag) for downstream use.
- [x] 4.2 Add a test helper `assert_requires_permission(client, url, method, permiso)` that verifies the endpoint returns 403 without the required permission.
- [x] 4.3 Add sample usage on the auth router's admin endpoints to demonstrate the guard (e.g., lock down logout/refresh endpoints with basic `authenticated` check — note: `authenticated` isn't a permission, just presence of `get_current_user`).

## 5. Admin CRUD Routers

- [x] 5.1 Create `app/api/v1/routers/admin.py` with:
    - `GET /api/admin/roles` — list all roles for the tenant (paginated).
    - `POST /api/admin/roles` — create new role (ADMIN only via guard).
    - `GET /api/admin/roles/{rol_id}` — get role detail.
    - `PUT /api/admin/roles/{rol_id}` — update role.
    - `DELETE /api/admin/roles/{rol_id}` — soft-delete role.
    - `GET /api/admin/permisos` — list all permissions (paginated).
    - `POST /api/admin/permisos` — create new permission.
    - `GET /api/admin/permisos/{permiso_id}` — get permission detail.
    - `PUT /api/admin/permisos/{permiso_id}` — update permission.
    - `DELETE /api/admin/permisos/{permiso_id}` — soft-delete permission.
    - `POST /api/admin/roles/{rol_id}/permisos` — assign permission to role.
    - `DELETE /api/admin/roles/{rol_id}/permisos/{permiso_id}` — remove permission from role.
    - All endpoints protected with `require_permission(Perm.ESTRUCTURA_GESTIONAR)` (ADMIN-level).
- [x] 5.2 Register the admin router in `app/main.py` with prefix.

## 6. Tests

- [x] 6.1 Test `PermissionResolver`: seed two roles with different permissions, verify union resolution, verify cache hit within same request, verify `(propio)` flag returned.
- [x] 6.2 Test `require_permission` dependency: user with permission → 200 (or pass-through), user without → 403.
- [x] 6.3 Test role union: user with PROFESOR and COORDINADOR roles gets permissions from both.
- [x] 6.4 Test `(propio)` behavior: PROFESOR gets `calificaciones:importar` with `es_propio=True`; verify the flag is available to the endpoint.
- [x] 6.5 Test admin CRUD for roles: create, read, update, soft-delete, verify tenant isolation.
- [x] 6.6 Test admin CRUD for permissions: create, read, update, soft-delete, verify unique `codigo` per tenant.
- [x] 6.7 Test admin CRUD for role-permission assignment: assign and remove, verify effective permissions update.
- [x] 6.8 Test migration seed data: verify all 7 roles exist, verify all matrix permissions are present, verify NEXO has zero permissions.
- [x] 6.9 Test multi-tenant isolation: same role `codigo` in two tenants are independent.
- [x] 6.10 Test soft-delete cascade: soft-deleting a role should not break existing `rol_permiso` references (use FK with `ON DELETE SET NULL` only if intended — prefer keeping the `rol_permiso` row intact since soft-delete doesn't remove the PK).
