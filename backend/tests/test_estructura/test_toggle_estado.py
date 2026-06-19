from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import cleanup_permission_cache
from tests.test_estructura.conftest import make_token


async def _create_carrera(client, token, codigo="CARR-TOGGLE"):
    resp = await client.post(
        "/api/admin/carreras",
        headers={"Authorization": f"Bearer {token}"},
        json={"codigo": codigo, "nombre": f"Carrera {codigo}"},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _create_cohorte(client, token, carrera_id, nombre="Cohorte TOGGLE"):
    resp = await client.post(
        "/api/admin/cohortes",
        headers={"Authorization": f"Bearer {token}"},
        json={"carrera_id": carrera_id, "nombre": nombre, "anio": 2025},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _create_materia(client, token, codigo="MAT-TOGGLE"):
    resp = await client.post(
        "/api/admin/materias",
        headers={"Authorization": f"Bearer {token}"},
        json={"codigo": codigo, "nombre": f"Materia {codigo}"},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _create_dictado(client, token, materia_id, carrera_id, cohorte_id):
    resp = await client.post(
        "/api/admin/dictados",
        headers={"Authorization": f"Bearer {token}"},
        json={"materia_id": materia_id, "carrera_id": carrera_id, "cohorte_id": cohorte_id},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


# ── Carrera toggle ───────────────────────────────────────────────────────


async def test_toggle_carrera_activa_to_inactiva_and_back(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)
    carrera_id = await _create_carrera(client, token, "CARR-TGL-1")

    toggle_inactiva = await client.patch(
        f"/api/admin/carreras/{carrera_id}/estado",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert toggle_inactiva.status_code == 200
    assert toggle_inactiva.json()["estado"] == "Inactiva"

    toggle_activa = await client.patch(
        f"/api/admin/carreras/{carrera_id}/estado",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert toggle_activa.status_code == 200
    assert toggle_activa.json()["estado"] == "Activa"


async def test_toggle_carrera_inactiva_con_cohortes_abiertas_returns_422(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)
    carrera_id = await _create_carrera(client, token, "CARR-TGL-2")
    await _create_cohorte(client, token, carrera_id, "Cohorte Abierta TGL")

    toggle_resp = await client.patch(
        f"/api/admin/carreras/{carrera_id}/estado",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert toggle_resp.status_code == 422
    detail = toggle_resp.json()["error"]["message"]
    assert "cohortes abiertas" in detail.lower()


async def test_toggle_carrera_inexistente_returns_404(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    resp = await client.patch(
        "/api/admin/carreras/00000000-0000-0000-0000-000000000000/estado",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


async def test_toggle_carrera_sin_permiso_returns_403(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, alumno_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(alumno_user)

    resp = await client.patch(
        "/api/admin/carreras/00000000-0000-0000-0000-000000000000/estado",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


# ── Cohorte toggle ───────────────────────────────────────────────────────


async def test_toggle_cohorte_activa_to_inactiva_and_back(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)
    carrera_id = await _create_carrera(client, token, "CARR-TGL-COH")
    cohorte_id = await _create_cohorte(client, token, carrera_id, "Cohorte TGL COH")

    toggle_inactiva = await client.patch(
        f"/api/admin/cohortes/{cohorte_id}/estado",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert toggle_inactiva.status_code == 200
    assert toggle_inactiva.json()["estado"] == "Inactiva"

    toggle_activa = await client.patch(
        f"/api/admin/cohortes/{cohorte_id}/estado",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert toggle_activa.status_code == 200
    assert toggle_activa.json()["estado"] == "Activa"


async def test_toggle_cohorte_inexistente_returns_404(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    resp = await client.patch(
        "/api/admin/cohortes/00000000-0000-0000-0000-000000000000/estado",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


# ── Materia toggle ────────────────────────────────────────────────────────


async def test_toggle_materia_activa_to_inactiva_and_back(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)
    materia_id = await _create_materia(client, token, "MAT-TGL-1")

    toggle_inactiva = await client.patch(
        f"/api/admin/materias/{materia_id}/estado",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert toggle_inactiva.status_code == 200
    assert toggle_inactiva.json()["estado"] == "Inactiva"

    toggle_activa = await client.patch(
        f"/api/admin/materias/{materia_id}/estado",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert toggle_activa.status_code == 200
    assert toggle_activa.json()["estado"] == "Activa"


async def test_toggle_materia_inexistente_returns_404(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    resp = await client.patch(
        "/api/admin/materias/00000000-0000-0000-0000-000000000000/estado",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


# ── Dictado toggle ────────────────────────────────────────────────────────


async def test_toggle_dictado_activo_to_inactivo_and_back(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)
    carrera_id = await _create_carrera(client, token, "CARR-TGL-DIC")
    materia_id = await _create_materia(client, token, "MAT-TGL-DIC")
    cohorte_id = await _create_cohorte(client, token, carrera_id, "Cohorte TGL DIC")
    dictado_id = await _create_dictado(client, token, materia_id, carrera_id, cohorte_id)

    toggle_inactivo = await client.patch(
        f"/api/admin/dictados/{dictado_id}/estado",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert toggle_inactivo.status_code == 200
    assert toggle_inactivo.json()["estado"] == "Inactivo"

    toggle_activo = await client.patch(
        f"/api/admin/dictados/{dictado_id}/estado",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert toggle_activo.status_code == 200
    assert toggle_activo.json()["estado"] == "Activo"


async def test_toggle_dictado_inexistente_returns_404(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    resp = await client.patch(
        "/api/admin/dictados/00000000-0000-0000-0000-000000000000/estado",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404
