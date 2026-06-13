"""6.1/6.2: multi-tenant isolation and cross-tenant uniqueness for
estructura academica (carreras/cohortes/materias/dictados)."""

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import cleanup_permission_cache, seed_permissions_for_tenant
from tests.test_estructura.conftest import _make_user, make_token


async def _seed_admin(db_session: AsyncSession, tenant, email: str):
    await seed_permissions_for_tenant(db_session, tenant.id)
    return await _make_user(db_session, tenant.id, email, ["ADMIN"])


# ── 6.2: same codigo/nombre across different tenants does not collide ──


async def test_same_codigo_carrera_across_tenants_does_not_collide(
    client: AsyncClient, db_session: AsyncSession, test_tenant, another_tenant
):
    cleanup_permission_cache()
    admin_a = await _seed_admin(db_session, test_tenant, "admin-a@multi.test")
    admin_b = await _seed_admin(db_session, another_tenant, "admin-b@multi.test")
    await db_session.commit()

    token_a = make_token(admin_a)
    token_b = make_token(admin_b)

    resp_a = await client.post(
        "/api/admin/carreras",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"codigo": "ING-INF", "nombre": "Ingeniería Informática"},
    )
    assert resp_a.status_code == 201

    resp_b = await client.post(
        "/api/admin/carreras",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"codigo": "ING-INF", "nombre": "Ingeniería Informática (tenant B)"},
    )
    assert resp_b.status_code == 201
    assert resp_b.json()["id"] != resp_a.json()["id"]


# ── 6.1: tenant A cannot see/edit/delete tenant B entities ──────────────


async def test_tenant_a_cannot_get_update_delete_tenant_b_carrera(
    client: AsyncClient, db_session: AsyncSession, test_tenant, another_tenant
):
    cleanup_permission_cache()
    admin_a = await _seed_admin(db_session, test_tenant, "admin-a2@multi.test")
    admin_b = await _seed_admin(db_session, another_tenant, "admin-b2@multi.test")
    await db_session.commit()

    token_a = make_token(admin_a)
    token_b = make_token(admin_b)

    create_b = await client.post(
        "/api/admin/carreras",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"codigo": "ING-SIS", "nombre": "Ingeniería en Sistemas"},
    )
    carrera_b_id = create_b.json()["id"]

    get_resp = await client.get(
        f"/api/admin/carreras/{carrera_b_id}",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert get_resp.status_code == 404

    put_resp = await client.put(
        f"/api/admin/carreras/{carrera_b_id}",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"estado": "Inactiva"},
    )
    assert put_resp.status_code == 404

    del_resp = await client.delete(
        f"/api/admin/carreras/{carrera_b_id}",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert del_resp.status_code == 404


# ── 6.1: cannot reference another tenant's carrera/cohorte/materia ──────


async def test_tenant_a_cannot_create_dictado_referencing_tenant_b_entities(
    client: AsyncClient, db_session: AsyncSession, test_tenant, another_tenant
):
    cleanup_permission_cache()
    admin_a = await _seed_admin(db_session, test_tenant, "admin-a3@multi.test")
    admin_b = await _seed_admin(db_session, another_tenant, "admin-b3@multi.test")
    await db_session.commit()

    token_a = make_token(admin_a)
    token_b = make_token(admin_b)

    # Tenant B's full set of entities
    carrera_b = await client.post(
        "/api/admin/carreras",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"codigo": "ING-B", "nombre": "Carrera B"},
    )
    carrera_b_id = carrera_b.json()["id"]

    materia_b = await client.post(
        "/api/admin/materias",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"codigo": "MAT-B", "nombre": "Materia B"},
    )
    materia_b_id = materia_b.json()["id"]

    cohorte_b = await client.post(
        "/api/admin/cohortes",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"carrera_id": carrera_b_id, "nombre": "2024", "anio": 2024},
    )
    cohorte_b_id = cohorte_b.json()["id"]

    # Tenant A tries to create a dictado referencing tenant B's entities.
    resp = await client.post(
        "/api/admin/dictados",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"materia_id": materia_b_id, "carrera_id": carrera_b_id, "cohorte_id": cohorte_b_id},
    )
    # Service-level lookups are tenant-scoped, so the referenced entities
    # are not found from tenant A's perspective -> 404.
    assert resp.status_code == 404


async def test_tenant_a_cannot_create_cohorte_referencing_tenant_b_carrera(
    client: AsyncClient, db_session: AsyncSession, test_tenant, another_tenant
):
    cleanup_permission_cache()
    admin_a = await _seed_admin(db_session, test_tenant, "admin-a4@multi.test")
    admin_b = await _seed_admin(db_session, another_tenant, "admin-b4@multi.test")
    await db_session.commit()

    token_a = make_token(admin_a)
    token_b = make_token(admin_b)

    carrera_b = await client.post(
        "/api/admin/carreras",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"codigo": "ING-B2", "nombre": "Carrera B2"},
    )
    carrera_b_id = carrera_b.json()["id"]

    resp = await client.post(
        "/api/admin/cohortes",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"carrera_id": carrera_b_id, "nombre": "2024", "anio": 2024},
    )
    assert resp.status_code == 404


# ── 6.1: listado acotado al tenant ──────────────────────────────────────


async def test_list_carreras_only_returns_own_tenant(
    client: AsyncClient, db_session: AsyncSession, test_tenant, another_tenant
):
    cleanup_permission_cache()
    admin_a = await _seed_admin(db_session, test_tenant, "admin-a5@multi.test")
    admin_b = await _seed_admin(db_session, another_tenant, "admin-b5@multi.test")
    await db_session.commit()

    token_a = make_token(admin_a)
    token_b = make_token(admin_b)

    await client.post(
        "/api/admin/carreras",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"codigo": "ING-LIST-A", "nombre": "Carrera Lista A"},
    )
    await client.post(
        "/api/admin/carreras",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"codigo": "ING-LIST-B", "nombre": "Carrera Lista B"},
    )

    list_a = await client.get(
        "/api/admin/carreras", headers={"Authorization": f"Bearer {token_a}"}
    )
    codigos_a = [c["codigo"] for c in list_a.json()]
    assert "ING-LIST-A" in codigos_a
    assert "ING-LIST-B" not in codigos_a
