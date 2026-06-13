from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import cleanup_permission_cache
from tests.test_estructura.conftest import make_token


async def test_create_materia_without_permission_returns_403(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, alumno_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(alumno_user)

    response = await client.post(
        "/api/admin/materias",
        headers={"Authorization": f"Bearer {token}"},
        json={"codigo": "MAT-101", "nombre": "Análisis Matemático I"},
    )
    assert response.status_code == 403


async def test_create_and_get_materia_with_admin(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    create_resp = await client.post(
        "/api/admin/materias",
        headers={"Authorization": f"Bearer {token}"},
        json={"codigo": "MAT-101", "nombre": "Análisis Matemático I"},
    )
    assert create_resp.status_code == 201
    body = create_resp.json()
    assert body["estado"] == "Activa"

    get_resp = await client.get(
        f"/api/admin/materias/{body['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_resp.status_code == 200


async def test_duplicate_materia_codigo_returns_422(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    await client.post(
        "/api/admin/materias",
        headers={"Authorization": f"Bearer {token}"},
        json={"codigo": "MAT-202", "nombre": "Física I"},
    )
    second = await client.post(
        "/api/admin/materias",
        headers={"Authorization": f"Bearer {token}"},
        json={"codigo": "MAT-202", "nombre": "Otra física"},
    )
    assert second.status_code == 422


async def test_delete_materia_soft_deletes(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    create_resp = await client.post(
        "/api/admin/materias",
        headers={"Authorization": f"Bearer {token}"},
        json={"codigo": "MAT-303", "nombre": "Química General"},
    )
    materia_id = create_resp.json()["id"]

    delete_resp = await client.delete(
        f"/api/admin/materias/{materia_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_resp.status_code == 200
    assert delete_resp.json()["deleted_at"] is True

    get_resp = await client.get(
        f"/api/admin/materias/{materia_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_resp.status_code == 404
