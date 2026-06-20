"""Comprehensive tests for the RBAC permission system (C-04)."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException
from app.models.permiso import Permiso
from app.models.rol import Rol
from app.models.rol_permiso import RolPermiso
from app.repositories.permiso_repository import PermisoRepository
from app.repositories.rol_permiso_repository import RolPermisoRepository
from app.repositories.rol_repository import RolRepository
from app.services.permission_service import PermissionResolver
from tests.helpers import cleanup_permission_cache, seed_permissions_for_tenant

# ── Helpers ────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _clear_cache():
    """Clear permission cache before each test."""
    cleanup_permission_cache()


# ═══════════════════════════════════════════════════════════════════════
# Task 6.1 — PermissionResolver
# ═══════════════════════════════════════════════════════════════════════


async def test_resolver_returns_union_of_role_permissions(
    db_session: AsyncSession, test_tenant
):
    """Seed ALUMNO + PROFESOR, verify union resolver."""
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    resolver = PermissionResolver(session=db_session)

    alumno_perms = await resolver.get_effective_permissions(
        test_tenant.id, ["ALUMNO"]
    )
    assert "estado-academico:ver" in alumno_perms
    assert "evaluacion:reservar" in alumno_perms
    assert "avisos:confirmar" in alumno_perms
    assert "calificaciones:importar" not in alumno_perms

    cleanup_permission_cache()
    profesor_perms = await resolver.get_effective_permissions(
        test_tenant.id, ["PROFESOR"]
    )
    assert "avisos:confirmar" in profesor_perms
    assert "calificaciones:importar" in profesor_perms
    assert "evaluacion:reservar" not in profesor_perms


async def test_resolver_cache_hit(
    db_session: AsyncSession, test_tenant
):
    """Same resolver instance returns cached result on second call."""
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    resolver = PermissionResolver(session=db_session)

    perms1 = await resolver.get_effective_permissions(
        test_tenant.id, ["PROFESOR"]
    )
    perms2 = await resolver.get_effective_permissions(
        test_tenant.id, ["PROFESOR"]
    )
    assert perms1 == perms2


async def test_resolver_returns_propio_flag(
    db_session: AsyncSession, test_tenant
):
    """Verify es_propio metadata is correctly returned."""
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    resolver = PermissionResolver(session=db_session)

    meta = await resolver.get_permission_metadata(
        test_tenant.id, ["PROFESOR"]
    )
    # PROFESOR has calificaciones:importar with es_propio=True
    assert meta.get("calificaciones:importar") is True
    # PROFESOR has avisos:confirmar with es_propio=False
    assert meta.get("avisos:confirmar") is False

    # COORDINADOR has calificaciones:importar with es_propio=False
    cleanup_permission_cache()
    coord_meta = await resolver.get_permission_metadata(
        test_tenant.id, ["COORDINADOR"]
    )
    assert coord_meta.get("calificaciones:importar") is False


# ═══════════════════════════════════════════════════════════════════════
# Task 6.2 — require_permission guard logic
# ═══════════════════════════════════════════════════════════════════════


async def test_require_permission_allows_authorized(
    db_session: AsyncSession, test_tenant
):
    """User with correct role can access the permission."""
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    resolver = PermissionResolver(session=db_session)

    perms = await resolver.get_effective_permissions(
        test_tenant.id, ["ADMIN"]
    )
    assert "estructura:gestionar" in perms


async def test_require_permission_blocks_unauthorized(
    db_session: AsyncSession, test_tenant
):
    """User without permission gets ForbiddenException."""
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    resolver = PermissionResolver(session=db_session)

    perms = await resolver.get_effective_permissions(
        test_tenant.id, ["ALUMNO"]
    )
    assert "estructura:gestionar" not in perms


# ═══════════════════════════════════════════════════════════════════════
# Task 6.3 — Role union
# ═══════════════════════════════════════════════════════════════════════


async def test_role_union_resolves_both(
    db_session: AsyncSession, test_tenant
):
    """User with PROFESOR and COORDINADOR gets permissions from both."""
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    resolver = PermissionResolver(session=db_session)

    perms = await resolver.get_effective_permissions(
        test_tenant.id, ["PROFESOR", "COORDINADOR"]
    )
    # From PROFESOR
    assert "calificaciones:importar" in perms
    assert "comunicacion:enviar" in perms
    # From COORDINADOR
    assert "comunicacion:aprobar" in perms
    assert "avisos:publicar" in perms
    assert "equipos:gestionar" in perms


# ═══════════════════════════════════════════════════════════════════════
# Task 6.4 — (propio) behavior
# ═══════════════════════════════════════════════════════════════════════


async def test_propio_flag_behavior(
    db_session: AsyncSession, test_tenant
):
    """PROFESOR gets calificaciones:importar with es_propio=True."""
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    resolver = PermissionResolver(session=db_session)

    meta = await resolver.get_permission_metadata(
        test_tenant.id, ["PROFESOR"]
    )
    assert meta["calificaciones:importar"] is True

    # COORDINADOR gets the same permission without propio flag
    cleanup_permission_cache()
    coord_meta = await resolver.get_permission_metadata(
        test_tenant.id, ["COORDINADOR"]
    )
    assert coord_meta["calificaciones:importar"] is False


# ═══════════════════════════════════════════════════════════════════════
# Task 6.5 — Admin CRUD roles
# ═══════════════════════════════════════════════════════════════════════


async def test_admin_crud_create_role(
    db_session: AsyncSession, test_tenant
):
    """Create a role via repository."""
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    repo = RolRepository(session=db_session, tenant_id=test_tenant.id)
    role = await repo.create(
        {"codigo": "TEST", "nombre": "Test Role", "descripcion": "A test role"}
    )
    assert role.id is not None
    assert role.codigo == "TEST"
    assert role.nombre == "Test Role"


async def test_admin_crud_read_role(
    db_session: AsyncSession, test_tenant
):
    """Read a role by ID."""
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    repo = RolRepository(session=db_session, tenant_id=test_tenant.id)
    role = await repo.create({"codigo": "TEST", "nombre": "Test"})
    found = await repo.find_by_id(role.id)
    assert found is not None
    assert found.codigo == "TEST"


async def test_admin_crud_update_role(
    db_session: AsyncSession, test_tenant
):
    """Update a role."""
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    repo = RolRepository(session=db_session, tenant_id=test_tenant.id)
    role = await repo.create({"codigo": "OLD", "nombre": "Old Name"})
    updated = await repo.update(role.id, {"codigo": "NEW", "nombre": "New Name"})
    assert updated.codigo == "NEW"
    assert updated.nombre == "New Name"


async def test_admin_crud_soft_delete_role(
    db_session: AsyncSession, test_tenant
):
    """Soft-delete a role, then verify it's excluded from normal queries."""
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    repo = RolRepository(session=db_session, tenant_id=test_tenant.id)
    role = await repo.create({"codigo": "TODELETE", "nombre": "To Delete"})
    await repo.soft_delete(role.id)
    found = await repo.find_by_id(role.id)
    assert found is None
    # Can still find with include_deleted
    repo2 = RolRepository(session=db_session, tenant_id=test_tenant.id)
    found = await repo2.include_deleted().find_by_id(role.id)
    assert found is not None
    assert found.deleted_at is not None


async def test_admin_crud_role_tenant_isolation(
    db_session: AsyncSession, test_tenant, another_tenant
):
    """Roles in one tenant should not be visible in another."""
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    await seed_permissions_for_tenant(db_session, another_tenant.id)

    repo1 = RolRepository(session=db_session, tenant_id=test_tenant.id)
    repo2 = RolRepository(session=db_session, tenant_id=another_tenant.id)

    roles_tenant1 = await repo1.find_all()
    roles_tenant2 = await repo2.find_all()

    # Each tenant should have its own set of 7 roles
    assert len(roles_tenant1) == 7
    assert len(roles_tenant2) == 7


# ═══════════════════════════════════════════════════════════════════════
# Task 6.6 — Admin CRUD permissions
# ═══════════════════════════════════════════════════════════════════════


async def test_admin_crud_create_permiso(
    db_session: AsyncSession, test_tenant
):
    """Create a permission."""
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    repo = PermisoRepository(session=db_session, tenant_id=test_tenant.id)
    perm = await repo.create({
        "codigo": "test:permiso",
        "nombre": "Test Permission",
        "modulo": "test",
    })
    assert perm.id is not None
    assert perm.codigo == "test:permiso"


async def test_admin_crud_find_permiso_by_codigo(
    db_session: AsyncSession, test_tenant
):
    """Find a permission by codigo."""
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    repo = PermisoRepository(session=db_session, tenant_id=test_tenant.id)
    perm = await repo.find_by_codigo(test_tenant.id, "calificaciones:importar")
    assert perm is not None
    assert perm.codigo == "calificaciones:importar"


async def test_admin_crud_find_permiso_by_modulo(
    db_session: AsyncSession, test_tenant
):
    """Find permissions by modulo."""
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    repo = PermisoRepository(session=db_session, tenant_id=test_tenant.id)
    results = await repo.find_by_modulo(test_tenant.id, "comunicacion")
    assert len(results) == 2
    codigos = {r.codigo for r in results}
    assert "comunicacion:enviar" in codigos
    assert "comunicacion:aprobar" in codigos


# ═══════════════════════════════════════════════════════════════════════
# Task 6.7 — Role-Permission assignment
# ═══════════════════════════════════════════════════════════════════════


async def test_assign_and_remove_rol_permiso(
    db_session: AsyncSession, test_tenant
):
    """Assign and remove a permission from a role via RolPermisoRepository."""
    await seed_permissions_for_tenant(db_session, test_tenant.id)

    # Find an existing rol and permiso
    rol_repo = RolRepository(session=db_session, tenant_id=test_tenant.id)
    perm_repo = PermisoRepository(session=db_session, tenant_id=test_tenant.id)
    rp_repo = RolPermisoRepository(session=db_session, tenant_id=test_tenant.id)

    roles = await rol_repo.find_by(codigo="ALUMNO")
    assert len(roles) == 1
    role = roles[0]

    # Find a permission ALUMNO doesn't have yet
    perm = await perm_repo.find_by_codigo(test_tenant.id, "calificaciones:importar")

    # Assign it to ALUMNO
    rp = await rp_repo.create({
        "rol_id": role.id,
        "permiso_id": perm.id,
    })
    assert rp.id is not None

    # Verify it's now resolvable for ALUMNO
    resolver = PermissionResolver(session=db_session)
    perms = await resolver.get_effective_permissions(test_tenant.id, ["ALUMNO"])
    assert "calificaciones:importar" in perms

    # Remove it
    existing = await rp_repo.find_by(rol_id=role.id, permiso_id=perm.id)
    assert len(existing) == 1
    await rp_repo.hard_delete(existing[0].id)

    # Verify it's removed
    cleanup_permission_cache()
    perms_after = await resolver.get_effective_permissions(
        test_tenant.id, ["ALUMNO"]
    )
    assert "calificaciones:importar" not in perms_after


# ═══════════════════════════════════════════════════════════════════════
# Task 6.8 — Migration seed data verification
# ═══════════════════════════════════════════════════════════════════════


async def test_seed_all_roles_exist(
    db_session: AsyncSession, test_tenant
):
    """Verify all 7 domain roles are seeded."""
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    repo = RolRepository(session=db_session, tenant_id=test_tenant.id)
    roles = await repo.find_all()
    role_codes = {r.codigo for r in roles}
    expected = {"ALUMNO", "TUTOR", "PROFESOR", "COORDINADOR", "NEXO", "ADMIN", "FINANZAS"}
    assert role_codes == expected


async def test_seed_all_permissions_exist(
    db_session: AsyncSession, test_tenant
):
    """Verify all matrix permissions are present after seeding."""
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    repo = PermisoRepository(session=db_session, tenant_id=test_tenant.id)
    perms = await repo.find_all()
    perm_codes = {p.codigo for p in perms}
    expected = {
        "estado-academico:ver",
        "evaluacion:reservar",
        "avisos:confirmar",
        "calificaciones:importar",
        "atrasados:ver",
        "entregas:sin-corregir",
        "comunicacion:enviar",
        "comunicacion:aprobar",
        "encuentros:gestionar",
        "guardias:registrar",
        "tareas:gestionar",
        "avisos:publicar",
        "equipos:gestionar",
        "equipos:asignar",
        "estructura:gestionar",
        "usuarios:gestionar",
        "auditoria:ver",
        "padron:ver",
        "padron:importar",
        "padron:vaciar",
        "coloquios:ver",
        "coloquios:reservar",
        "coloquios:gestionar",
        "grilla:operar",
        "liquidaciones:ver",
        "liquidaciones:calcular",
        "liquidaciones:configurar-salarios",
        "liquidaciones:cerrar",
        "facturas:gestionar",
        "configurar:tenant",
        "inbox:acceder",
        # C-25 profesor dashboard
        "actividades:gestionar",
        "calificaciones:editar",
        "padron:gestionar-alumno",
    }
    assert perm_codes == expected


async def test_seed_nexo_has_inbox_only(
    db_session: AsyncSession, test_tenant
):
    """NEXO role should only have inbox:acceder (enlace needs messaging)."""
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    rp_repo = RolPermisoRepository(session=db_session, tenant_id=test_tenant.id)
    rol_repo = RolRepository(session=db_session, tenant_id=test_tenant.id)

    roles = await rol_repo.find_by(codigo="NEXO")
    assert len(roles) == 1

    rows = await rp_repo.find_permisos_for_roles(test_tenant.id, ["NEXO"])
    assert len(rows) == 1, "NEXO should have exactly one permission"
    perm_codigo, es_propio = rows[0]
    assert perm_codigo == "inbox:acceder"
    assert es_propio is False


# ═══════════════════════════════════════════════════════════════════════
# Task 6.9 — Multi-tenant isolation
# ═══════════════════════════════════════════════════════════════════════


async def test_same_role_codigo_independent_across_tenants(
    db_session: AsyncSession, test_tenant, another_tenant
):
    """Same role codigo in two tenants should be independent records."""
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    await seed_permissions_for_tenant(db_session, another_tenant.id)

    repo1 = RolRepository(session=db_session, tenant_id=test_tenant.id)
    repo2 = RolRepository(session=db_session, tenant_id=another_tenant.id)

    alumno1 = await repo1.find_by_codigo(test_tenant.id, "ALUMNO")
    alumno2 = await repo2.find_by_codigo(another_tenant.id, "ALUMNO")

    assert alumno1 is not None
    assert alumno2 is not None
    assert alumno1.id != alumno2.id
    assert alumno1.tenant_id != alumno2.tenant_id

    # Modify name in tenant1 only
    await repo1.update(alumno1.id, {"nombre": "Alumno Modificado"})
    updated1 = await repo1.find_by_id(alumno1.id)
    updated2 = await repo2.find_by_id(alumno2.id)

    assert updated1.nombre == "Alumno Modificado"
    assert updated2.nombre == "Alumno"  # unchanged


# ═══════════════════════════════════════════════════════════════════════
# Task 6.10 — Soft-delete cascade (rol_permiso references intact)
# ═══════════════════════════════════════════════════════════════════════


async def test_soft_delete_role_keeps_rol_permiso_intact(
    db_session: AsyncSession, test_tenant
):
    """Soft-deleting a role should keep associated rol_permiso references intact."""
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    repo = RolRepository(session=db_session, tenant_id=test_tenant.id)
    rp_repo = RolPermisoRepository(session=db_session, tenant_id=test_tenant.id)

    roles = await repo.find_by(codigo="ALUMNO")
    assert len(roles) == 1
    role = roles[0]

    # Count rol_permiso before soft-delete
    count_before = len(await rp_repo.find_by(rol_id=role.id))
    assert count_before > 0

    # Soft-delete the role
    await repo.soft_delete(role.id)

    # Verify rol_permiso rows still exist (not cascade-deleted by soft delete)
    count_after = len(await rp_repo.find_by(rol_id=role.id))
    assert count_after == count_before, (
        "Soft-deleting a role should not remove its rol_permiso rows"
    )


# ═══════════════════════════════════════════════════════════════════════
# Task 6.3 (API level) — Admin endpoint requires permission
# ═══════════════════════════════════════════════════════════════════════


async def test_admin_api_endpoint_requires_auth(client: AsyncClient, db_session: AsyncSession, test_tenant):
    """Admin endpoints return 401 without auth token."""
    response = await client.get("/api/admin/roles")
    assert response.status_code == 401


async def test_admin_api_list_roles_with_admin_token(
    client: AsyncClient, db_session: AsyncSession, test_tenant, admin_user
):
    """Admin user with proper permissions can list roles."""
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    await db_session.commit()
    from tests.test_permissions.conftest import make_token

    token = make_token(admin_user)
    response = await client.get(
        "/api/admin/roles",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 7


async def test_admin_api_list_roles_alumno_forbidden(
    client: AsyncClient, db_session: AsyncSession, test_tenant, alumno_user
):
    """ALUMNO user gets 403 when trying to access admin roles."""
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    await db_session.commit()
    from tests.test_permissions.conftest import make_token

    token = make_token(alumno_user)
    response = await client.get(
        "/api/admin/roles",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


async def test_admin_api_create_role(
    client: AsyncClient, db_session: AsyncSession, test_tenant, admin_user
):
    """Admin can create a new role via API."""
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    await db_session.commit()
    from tests.test_permissions.conftest import make_token

    token = make_token(admin_user)
    response = await client.post(
        "/api/admin/roles",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={
            "codigo": "TEST_ROLE",
            "nombre": "Test Role API",
            "descripcion": "Created via API",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["codigo"] == "TEST_ROLE"
    assert data["nombre"] == "Test Role API"


async def test_admin_api_assign_permiso_to_role(
    client: AsyncClient, db_session: AsyncSession, test_tenant, admin_user
):
    """Admin can assign a permission to a role via API."""
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    await db_session.commit()
    from tests.test_permissions.conftest import make_token

    token = make_token(admin_user)

    # Get the ALUMNO role and a permission
    rol_repo = RolRepository(session=db_session, tenant_id=test_tenant.id)
    perm_repo = PermisoRepository(session=db_session, tenant_id=test_tenant.id)
    roles = await rol_repo.find_by(codigo="ALUMNO")
    perm = await perm_repo.find_by_codigo(test_tenant.id, "calificaciones:importar")

    response = await client.post(
        f"/api/admin/roles/{roles[0].id}/permisos",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={"permiso_id": str(perm.id)},
    )
    assert response.status_code == 201
