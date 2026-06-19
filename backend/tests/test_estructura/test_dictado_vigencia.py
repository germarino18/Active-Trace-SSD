from datetime import date, timedelta

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import cleanup_permission_cache
from tests.test_estructura.conftest import make_token


async def _create_carrera(client, token, codigo="CAR-VIG"):
    resp = await client.post(
        "/api/admin/carreras",
        headers={"Authorization": f"Bearer {token}"},
        json={"codigo": codigo, "nombre": f"Carrera {codigo}"},
    )
    assert resp.status_code == 201
    return resp.json()


async def _create_materia(client, token, codigo="MAT-VIG"):
    resp = await client.post(
        "/api/admin/materias",
        headers={"Authorization": f"Bearer {token}"},
        json={"codigo": codigo, "nombre": f"Materia {codigo}"},
    )
    assert resp.status_code == 201
    return resp.json()


async def _create_cohorte(client, token, carrera_id, nombre="Cohorte Vigencia"):
    resp = await client.post(
        "/api/admin/cohortes",
        headers={"Authorization": f"Bearer {token}"},
        json={"carrera_id": carrera_id, "nombre": nombre, "anio": 2025},
    )
    assert resp.status_code == 201
    return resp.json()


# ── Creación de dictado sin vigencia ─────────────────────────────────────


async def test_create_dictado_sin_vigencia(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)
    carrera = await _create_carrera(client, token, "CAR-VIG-1")
    materia = await _create_materia(client, token, "MAT-VIG-1")
    cohorte = await _create_cohorte(client, token, carrera["id"], "Coh Sin Vigencia")

    resp = await client.post(
        "/api/admin/dictados",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "materia_id": materia["id"],
            "carrera_id": carrera["id"],
            "cohorte_id": cohorte["id"],
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["vig_desde"] is None
    assert body["vig_hasta"] is None
    assert body["estado"] == "Activo"


# ── Creación de dictado con vigencia ─────────────────────────────────────


async def test_create_dictado_con_vigencia(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)
    carrera = await _create_carrera(client, token, "CAR-VIG-2")
    materia = await _create_materia(client, token, "MAT-VIG-2")
    cohorte = await _create_cohorte(client, token, carrera["id"], "Coh Con Vigencia")

    today = date.today()
    vig_desde = today - timedelta(days=30)
    vig_hasta = today + timedelta(days=365)

    resp = await client.post(
        "/api/admin/dictados",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "materia_id": materia["id"],
            "carrera_id": carrera["id"],
            "cohorte_id": cohorte["id"],
            "vig_desde": vig_desde.isoformat(),
            "vig_hasta": vig_hasta.isoformat(),
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["vig_desde"] == vig_desde.isoformat()
    assert body["vig_hasta"] == vig_hasta.isoformat()


# ── Actualización de vigencia en dictado ──────────────────────────────────


async def test_update_dictado_vigencia(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)
    carrera = await _create_carrera(client, token, "CAR-VIG-3")
    materia = await _create_materia(client, token, "MAT-VIG-3")
    cohorte = await _create_cohorte(client, token, carrera["id"], "Coh Update Vig")

    create_resp = await client.post(
        "/api/admin/dictados",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "materia_id": materia["id"],
            "carrera_id": carrera["id"],
            "cohorte_id": cohorte["id"],
        },
    )
    dictado_id = create_resp.json()["id"]

    today = date.today()
    new_vig_desde = today - timedelta(days=60)
    new_vig_hasta = today + timedelta(days=180)

    update_resp = await client.put(
        f"/api/admin/dictados/{dictado_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "vig_desde": new_vig_desde.isoformat(),
            "vig_hasta": new_vig_hasta.isoformat(),
        },
    )
    assert update_resp.status_code == 200
    body = update_resp.json()
    assert body["vig_desde"] == new_vig_desde.isoformat()
    assert body["vig_hasta"] == new_vig_hasta.isoformat()


async def test_update_dictado_quitar_vigencia(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)
    carrera = await _create_carrera(client, token, "CAR-VIG-4")
    materia = await _create_materia(client, token, "MAT-VIG-4")
    cohorte = await _create_cohorte(client, token, carrera["id"], "Coh Quitar Vig")

    today = date.today()
    create_resp = await client.post(
        "/api/admin/dictados",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "materia_id": materia["id"],
            "carrera_id": carrera["id"],
            "cohorte_id": cohorte["id"],
            "vig_desde": (today - timedelta(days=30)).isoformat(),
            "vig_hasta": (today + timedelta(days=30)).isoformat(),
        },
    )
    dictado_id = create_resp.json()["id"]

    update_resp = await client.put(
        f"/api/admin/dictados/{dictado_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "vig_desde": None,
            "vig_hasta": None,
        },
    )
    assert update_resp.status_code == 200
    body = update_resp.json()
    assert body["vig_desde"] is None
    assert body["vig_hasta"] is None


# ── Dictado response incluye vigencia ─────────────────────────────────────


async def test_get_dictado_incluye_vigencia(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)
    carrera = await _create_carrera(client, token, "CAR-VIG-5")
    materia = await _create_materia(client, token, "MAT-VIG-5")
    cohorte = await _create_cohorte(client, token, carrera["id"], "Coh Get Vig")

    create_resp = await client.post(
        "/api/admin/dictados",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "materia_id": materia["id"],
            "carrera_id": carrera["id"],
            "cohorte_id": cohorte["id"],
            "vig_desde": "2025-01-01",
            "vig_hasta": "2025-12-31",
        },
    )
    dictado_id = create_resp.json()["id"]

    get_resp = await client.get(
        f"/api/admin/dictados/{dictado_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_resp.status_code == 200
    body = get_resp.json()
    assert body["vig_desde"] == "2025-01-01"
    assert body["vig_hasta"] == "2025-12-31"
