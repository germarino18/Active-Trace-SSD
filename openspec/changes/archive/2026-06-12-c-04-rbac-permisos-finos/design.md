## Context

activia-trace has identity (C-03: JWT auth, user model, refresh rotation) and multi-tenant infrastructure (C-02: Tenant, BaseRepository with tenant scoping), but no authorization layer. The JWT currently carries a raw `roles` array (e.g., `["PROFESOR", "COORDINADOR"]`), but no per-endpoint permission enforcement exists. Downstream changes (C-05 audit-log, C-06 estructura-academica, C-07 usuarios) depend on `require_permission` being ready.

The domain permission matrix is fully specified in `03_actores_y_roles.md` §3.3: 7 roles × 18 capabilities, with `(propio)` scoping for several PROFESOR/TUTOR permissions. Roles must be administrable (not hardcoded) per tenant.

### Constraints
- All permissions resolved server-side per request, NOT stored in JWT (see `08_arquitectura_propuesta.md` §3.1: "Los permisos se resuelven server-side en cada petición, nunca se almacenan en el token.")
- Fail-closed: no explicit permission → 403
- Tenant-scoped: permissions always filtered by `tenant_id`
- Soft-delete: roles and permissions can be deactivated, never hard-deleted

## Goals / Non-Goals

**Goals:**
- Database tables `rol`, `permiso`, `rol_permiso` with tenant isolation and soft delete
- Seed 7 domain roles + permission matrix as data (not code)
- `require_permission("modulo:accion")` FastAPI dependency that checks effective permissions server-side
- Resolution includes ALL active roles of the user (union), tenant-scoped
- `(propio)` modifier tracked as a flag on `rol_permiso`; enforcement delegated to the endpoint/service via `get_current_user` context
- Admin CRUD endpoints for roles and permissions (`POST/GET/PUT/DELETE /api/admin/roles`, same for `/api/admin/permisos`)
- Migration 003 with seed data for the base permission matrix
- Permission lookup is cached per-request (not per-endpoint) to avoid N+1 queries within a single request

**Non-Goals:**
- Time-bound permission resolution via `Asignacion.vigencia` (the `Asignacion` model doesn't exist yet — C-07). This change seeds roles/permisos but permission checks assume the user's role assignments are currently valid. When C-07 lands, the resolver will add the date filter.
- Permission inheritance or hierarchy (e.g., ADMIN automatically gets all permissions — ADMIN must have explicit entries in the matrix)
- UI for role/permission management (C-21 frontend)
- Audit log integration (C-05)
- Impersonation support (C-05)

## Decisions

### D1: Permission matrix as DB data, not code
**Chosen**: Three tables (`rol`, `permiso`, `rol_permiso`) with seed data. The matrix is fully administrable: an admin can add custom roles, assign new permission combinations, or deactivate rows without deployments.
**Alternatives considered**:
- *Python enums + dicts*: faster but require code changes for any matrix update. Rejected because the KB explicitly requires administrable catalog.
- *JSONB column on a single config table*: simpler schema but harder to query, index, and maintain referential integrity.

### D2: `require_permission` is a FastAPI dependency (not decorator)
**Chosen**: `async def require_permission(permiso: str) -> None` as a dependency that raises `ForbiddenException` if the user lacks the permission.
```python
@router.get("/calificaciones", dependencies=[Depends(require_permission("calificaciones:importar"))])
```
**Alternatives considered**:
- *Decorator on router functions*: adds coupling to the framework, harder to test in isolation.
- *Middleware*: would need to inspect route metadata; more complex and harder to parameterize per-endpoint.
- *Parametrized dependency with `fastapi.Depends()`*: idiomatic, composable, testable, and works with FastAPI's OpenAPI generation.

### D3: `(propio)` scope is a flag + convention, not separate permissions
**Chosen**: `rol_permiso` has a boolean `es_propio` column. The resolver returns the permission with a flag. The endpoint or service checks `es_propio` and filters data to `current_user.user_id`. This avoids doubling the permission catalog (e.g., `calificaciones:importar_propias` vs `calificaciones:importar`).
**Enforcement**: The `require_permission` dependency returns metadata about whether the permission is `(propio)`. A helper `assert_not_propio()` or the endpoint's own logic handles the data-level filter. This is documented as a pattern, not auto-enforced — some endpoints may have legitimate use for `(propio)` data access (e.g., COORDINADOR seeing all).

### D4: Permission resolution cached per-request
**Chosen**: The resolver fetches all `rol_permiso` rows for the user's roles once per request, cached in a `contextvars`-backed cache in the `core/permissions.py` module. Subsequent `require_permission` calls within the same request hit the cache.
**Rationale**: A single request may call `require_permission` multiple times (e.g., a POST handler that also reads related data). Without caching, each call triggers a DB query.

### D5: Permission constants in `core/permissions.py` for type safety
**Chosen**: While the matrix lives in the DB, the permissions used in `require_permission()` calls are also defined as string constants in `core/permissions.py`:
```python
class Perm:
    CALIFICACIONES_IMPORTAR = "calificaciones:importar"
    ATRASADOS_VER = "atrasados:ver"
    COMUNICACION_ENVIAR = "comunicacion:enviar"
    # ...
```
This prevents typos in endpoint declarations while keeping the source of truth in the DB.

### D6: NEXO role seeded with minimal permissions
**Chosen**: NEXO is seeded as a role with no permissions initially (pending PA-25 resolution in `10_preguntas_abiertas.md`). The migration inserts the role row but no `rol_permiso` entries for it. An admin can assign permissions later via the CRUD API.
**Rationale**: NEXO exists in the role catalog but its operational semantics are undefined (PA-25). Seeding empty avoids shipping wrong permissions.

## Risks / Trade-offs

- **Risk**: Permission query becomes expensive as matrix grows (7 roles × 18 permissions = 126 rows, trivially small). → Mitigation: per-request cache + single query with JOIN, not N queries.
- **Risk**: Two-phase migration: the seed data depends on UUID PKs. → Mitigation: use `op.execute()` with explicit UUIDs in the migration, or use a separate migration that inserts seed data after the table creation migration.
- **Risk**: `(propio)` enforcement is manual (convention, not compiler-checked). → Mitigation: code review and tests must verify that every endpoint using a `(propio)` permission actually filters by `user_id`.
- **Trade-off**: Permission checks don't use `Asignacion.vigencia` yet. When C-07 lands, the resolver needs a join or filter addition. The resolver is designed as a single method so the change is localized.
- **Trade-off**: Role names are stored as VARCHAR but referenced in code by string constants. A typo in a seed's `codigo` column would silently break authorization. → Mitigation: tests that verify the seed data contains all expected role codes.
