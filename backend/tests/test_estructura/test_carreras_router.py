from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import cleanup_permission_cache
from tests.test_estructura.conftest import make_token


async def test_create_carrera_without_permission_returns_403(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, alumno_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(alumno_user)

    response = await client.post(
        "/api/admin/carreras",
        headers={"Authorization": f"Bearer {token}"},
        json={"codigo": "ING-INF", "nombre": "Ingeniería Informática"},
    )

    assert response.status_code == 403


async def test_create_and_get_carrera_with_admin_returns_201_and_200(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    create_resp = await client.post(
        "/api/admin/carreras",
        headers={"Authorization": f"Bearer {token}"},
        json={"codigo": "ING-INF", "nombre": "Ingeniería Informática"},
    )
    assert create_resp.status_code == 201
    body = create_resp.json()
    assert body["codigo"] == "ING-INF"
    assert body["estado"] == "Activa"
    assert body["tenant_id"] == str(seeded_tenant.id)

    get_resp = await client.get(
        f"/api/admin/carreras/{body['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == body["id"]


async def test_get_carrera_from_other_tenant_returns_404(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_tenant,
    admin_user,
    another_tenant_admin,
):
    cleanup_permission_cache()
    await db_session.commit()
    token_a = make_token(admin_user)
    token_b = make_token(another_tenant_admin)

    create_resp = await client.post(
        "/api/admin/carreras",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"codigo": "ING-INF", "nombre": "Ingeniería Informática"},
    )
    assert create_resp.status_code == 201
    carrera_id = create_resp.json()["id"]

    get_resp = await client.get(
        f"/api/admin/carreras/{carrera_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert get_resp.status_code == 404


async def test_update_carrera_estado_inactiva(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    create_resp = await client.post(
        "/api/admin/carreras",
        headers={"Authorization": f"Bearer {token}"},
        json={"codigo": "ING-SIS", "nombre": "Ingeniería en Sistemas"},
    )
    carrera_id = create_resp.json()["id"]

    update_resp = await client.put(
        f"/api/admin/carreras/{carrera_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"estado": "Inactiva"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["estado"] == "Inactiva"


async def test_delete_carrera_soft_deletes(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    create_resp = await client.post(
        "/api/admin/carreras",
        headers={"Authorization": f"Bearer {token}"},
        json={"codigo": "ING-IND", "nombre": "Ingeniería Industrial"},
    )
    carrera_id = create_resp.json()["id"]

    delete_resp = await client.delete(
        f"/api/admin/carreras/{carrera_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_resp.status_code == 200
    assert delete_resp.json()["deleted_at"] is True

    get_resp = await client.get(
        f"/api/admin/carreras/{carrera_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_resp.status_code == 404


async def test_duplicate_codigo_returns_422(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    await client.post(
        "/api/admin/carreras",
        headers={"Authorization": f"Bearer {token}"},
        json={"codigo": "ING-CIV", "nombre": "Ingeniería Civil"},
    )

    second = await client.post(
        "/api/admin/carreras",
        headers={"Authorization": f"Bearer {token}"},
        json={"codigo": "ING-CIV", "nombre": "Otra ingeniería civil"},
    )
    assert second.status_code == 422


async def test_list_carreras_scoped_to_tenant(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_tenant,
    admin_user,
    another_tenant_admin,
):
    cleanup_permission_cache()
    await db_session.commit()
    token_a = make_token(admin_user)
    token_b = make_token(another_tenant_admin)

    await client.post(
        "/api/admin/carreras",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"codigo": "ING-INF", "nombre": "Ingeniería Informática"},
    )

    list_b = await client.get(
        "/api/admin/carreras",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert list_b.status_code == 200
    assert all(c["tenant_id"] != str(seeded_tenant.id) for c in list_b.json())
