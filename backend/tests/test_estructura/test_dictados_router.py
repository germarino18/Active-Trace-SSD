from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import cleanup_permission_cache
from tests.test_estructura.conftest import make_token


async def _create_carrera(client: AsyncClient, token: str, codigo: str) -> str:
    resp = await client.post(
        "/api/admin/carreras",
        headers={"Authorization": f"Bearer {token}"},
        json={"codigo": codigo, "nombre": f"Carrera {codigo}"},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _create_materia(client: AsyncClient, token: str, codigo: str) -> str:
    resp = await client.post(
        "/api/admin/materias",
        headers={"Authorization": f"Bearer {token}"},
        json={"codigo": codigo, "nombre": f"Materia {codigo}"},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _create_cohorte(client: AsyncClient, token: str, carrera_id: str, nombre: str) -> str:
    resp = await client.post(
        "/api/admin/cohortes",
        headers={"Authorization": f"Bearer {token}"},
        json={"carrera_id": carrera_id, "nombre": nombre, "anio": 2024},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def test_create_dictado_without_permission_returns_403(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, alumno_user
):
    cleanup_permission_cache()
    await db_session.commit()
    admin_token = make_token(admin_user)
    carrera_id = await _create_carrera(client, admin_token, "ING-D1")
    materia_id = await _create_materia(client, admin_token, "MAT-D1")
    cohorte_id = await _create_cohorte(client, admin_token, carrera_id, "2024-D1")

    alumno_token = make_token(alumno_user)
    resp = await client.post(
        "/api/admin/dictados",
        headers={"Authorization": f"Bearer {alumno_token}"},
        json={"materia_id": materia_id, "carrera_id": carrera_id, "cohorte_id": cohorte_id},
    )
    assert resp.status_code == 403


async def test_create_and_get_dictado_with_admin(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)
    carrera_id = await _create_carrera(client, token, "ING-D2")
    materia_id = await _create_materia(client, token, "MAT-D2")
    cohorte_id = await _create_cohorte(client, token, carrera_id, "2024-D2")

    create_resp = await client.post(
        "/api/admin/dictados",
        headers={"Authorization": f"Bearer {token}"},
        json={"materia_id": materia_id, "carrera_id": carrera_id, "cohorte_id": cohorte_id},
    )
    assert create_resp.status_code == 201
    body = create_resp.json()
    assert body["estado"] == "Activo"

    get_resp = await client.get(
        f"/api/admin/dictados/{body['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_resp.status_code == 200


async def test_dictado_terna_duplicada_returns_422(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)
    carrera_id = await _create_carrera(client, token, "ING-D3")
    materia_id = await _create_materia(client, token, "MAT-D3")
    cohorte_id = await _create_cohorte(client, token, carrera_id, "2024-D3")

    payload = {"materia_id": materia_id, "carrera_id": carrera_id, "cohorte_id": cohorte_id}
    first = await client.post(
        "/api/admin/dictados", headers={"Authorization": f"Bearer {token}"}, json=payload
    )
    assert first.status_code == 201

    second = await client.post(
        "/api/admin/dictados", headers={"Authorization": f"Bearer {token}"}, json=payload
    )
    assert second.status_code == 422


async def test_dictado_inconsistent_carrera_cohorte_returns_422(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)
    carrera_id = await _create_carrera(client, token, "ING-D4")
    otra_carrera_id = await _create_carrera(client, token, "ING-D4B")
    materia_id = await _create_materia(client, token, "MAT-D4")
    cohorte_id = await _create_cohorte(client, token, carrera_id, "2024-D4")

    resp = await client.post(
        "/api/admin/dictados",
        headers={"Authorization": f"Bearer {token}"},
        json={"materia_id": materia_id, "carrera_id": otra_carrera_id, "cohorte_id": cohorte_id},
    )
    assert resp.status_code == 422


async def test_dictado_on_inactive_materia_returns_422(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)
    carrera_id = await _create_carrera(client, token, "ING-D5")
    materia_id = await _create_materia(client, token, "MAT-D5")
    cohorte_id = await _create_cohorte(client, token, carrera_id, "2024-D5")

    await client.put(
        f"/api/admin/materias/{materia_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"estado": "Inactiva"},
    )

    resp = await client.post(
        "/api/admin/dictados",
        headers={"Authorization": f"Bearer {token}"},
        json={"materia_id": materia_id, "carrera_id": carrera_id, "cohorte_id": cohorte_id},
    )
    assert resp.status_code == 422
