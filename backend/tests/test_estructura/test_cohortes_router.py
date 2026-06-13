from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import cleanup_permission_cache
from tests.test_estructura.conftest import make_token


async def _create_carrera(client: AsyncClient, token: str, codigo: str = "ING-INF") -> str:
    resp = await client.post(
        "/api/admin/carreras",
        headers={"Authorization": f"Bearer {token}"},
        json={"codigo": codigo, "nombre": "Ingeniería Informática"},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def test_create_cohorte_without_permission_returns_403(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, alumno_user
):
    cleanup_permission_cache()
    await db_session.commit()
    admin_token = make_token(admin_user)
    carrera_id = await _create_carrera(client, admin_token)

    alumno_token = make_token(alumno_user)
    response = await client.post(
        "/api/admin/cohortes",
        headers={"Authorization": f"Bearer {alumno_token}"},
        json={"carrera_id": carrera_id, "nombre": "2024", "anio": 2024},
    )
    assert response.status_code == 403


async def test_create_and_get_cohorte_with_admin(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)
    carrera_id = await _create_carrera(client, token)

    create_resp = await client.post(
        "/api/admin/cohortes",
        headers={"Authorization": f"Bearer {token}"},
        json={"carrera_id": carrera_id, "nombre": "2024", "anio": 2024},
    )
    assert create_resp.status_code == 201
    body = create_resp.json()
    assert body["carrera_id"] == carrera_id
    assert body["estado"] == "Activa"

    get_resp = await client.get(
        f"/api/admin/cohortes/{body['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_resp.status_code == 200


async def test_duplicate_cohorte_nombre_in_carrera_returns_422(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)
    carrera_id = await _create_carrera(client, token, codigo="ING-SIS")

    await client.post(
        "/api/admin/cohortes",
        headers={"Authorization": f"Bearer {token}"},
        json={"carrera_id": carrera_id, "nombre": "2024", "anio": 2024},
    )
    second = await client.post(
        "/api/admin/cohortes",
        headers={"Authorization": f"Bearer {token}"},
        json={"carrera_id": carrera_id, "nombre": "2024", "anio": 2024},
    )
    assert second.status_code == 422


async def test_open_cohorte_on_inactive_carrera_returns_422(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)
    carrera_id = await _create_carrera(client, token, codigo="ING-MEC")

    await client.put(
        f"/api/admin/carreras/{carrera_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"estado": "Inactiva"},
    )

    resp = await client.post(
        "/api/admin/cohortes",
        headers={"Authorization": f"Bearer {token}"},
        json={"carrera_id": carrera_id, "nombre": "2024", "anio": 2024},
    )
    assert resp.status_code == 422
