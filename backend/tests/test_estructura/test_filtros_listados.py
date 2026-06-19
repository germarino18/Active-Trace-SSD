from datetime import date, timedelta

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import cleanup_permission_cache
from tests.test_estructura.conftest import make_token


async def _create_carrera(client, token, codigo, nombre=None):
    resp = await client.post(
        "/api/admin/carreras",
        headers={"Authorization": f"Bearer {token}"},
        json={"codigo": codigo, "nombre": nombre or f"Carrera {codigo}"},
    )
    assert resp.status_code == 201
    return resp.json()


async def _create_materia(client, token, codigo, nombre=None):
    resp = await client.post(
        "/api/admin/materias",
        headers={"Authorization": f"Bearer {token}"},
        json={"codigo": codigo, "nombre": nombre or f"Materia {codigo}"},
    )
    assert resp.status_code == 201
    return resp.json()


async def _create_cohorte(client, token, carrera_id, nombre, anio=2025):
    resp = await client.post(
        "/api/admin/cohortes",
        headers={"Authorization": f"Bearer {token}"},
        json={"carrera_id": carrera_id, "nombre": nombre, "anio": anio},
    )
    assert resp.status_code == 201
    return resp.json()


async def _create_dictado(client, token, materia_id, carrera_id, cohorte_id):
    resp = await client.post(
        "/api/admin/dictados",
        headers={"Authorization": f"Bearer {token}"},
        json={"materia_id": materia_id, "carrera_id": carrera_id, "cohorte_id": cohorte_id},
    )
    assert resp.status_code == 201
    return resp.json()


# ── Carreras filters ─────────────────────────────────────────────────────


async def test_list_carreras_filtro_activa(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    carrera_a = await _create_carrera(client, token, "CAR-FLT-A", "Activa Filter")
    carrera_b = await _create_carrera(client, token, "CAR-FLT-I", "Inactiva Filter")
    await client.put(
        f"/api/admin/carreras/{carrera_b['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json={"estado": "Inactiva"},
    )

    resp_activas = await client.get(
        "/api/admin/carreras?activa=true",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_activas.status_code == 200
    ids_activas = {c["id"] for c in resp_activas.json()}
    assert carrera_a["id"] in ids_activas
    assert carrera_b["id"] not in ids_activas

    resp_inactivas = await client.get(
        "/api/admin/carreras?activa=false",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_inactivas.status_code == 200
    ids_inactivas = {c["id"] for c in resp_inactivas.json()}
    assert carrera_a["id"] not in ids_inactivas
    assert carrera_b["id"] in ids_inactivas


async def test_list_carreras_filtro_q(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    await _create_carrera(client, token, "ING-INF", "Ingeniería Informática")
    await _create_carrera(client, token, "ING-CIV", "Ingeniería Civil")
    await _create_carrera(client, token, "LIC-ADM", "Licenciatura en Administración")

    resp = await client.get(
        "/api/admin/carreras?q=Ingeniería",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    nombres = {c["nombre"] for c in resp.json()}
    assert "Ingeniería Informática" in nombres
    assert "Ingeniería Civil" in nombres
    assert "Licenciatura en Administración" not in nombres


async def test_list_carreras_filtro_q_por_codigo(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    await _create_carrera(client, token, "ING-INF")
    await _create_carrera(client, token, "LIC-ADM")

    resp = await client.get(
        "/api/admin/carreras?q=ING",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    codigos = {c["codigo"] for c in resp.json()}
    assert "ING-INF" in codigos
    assert "LIC-ADM" not in codigos


# ── Cohortes filters ─────────────────────────────────────────────────────


async def test_list_cohortes_filtro_activa(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)
    carrera = await _create_carrera(client, token, "CAR-COH-FLT")

    coh_activa = await _create_cohorte(client, token, carrera["id"], "Cohorte Activa F")
    coh_inactiva = await _create_cohorte(client, token, carrera["id"], "Cohorte Inactiva F")
    await client.patch(
        f"/api/admin/cohortes/{coh_inactiva['id']}/estado",
        headers={"Authorization": f"Bearer {token}"},
    )

    resp_activas = await client.get(
        "/api/admin/cohortes?activa=true",
        headers={"Authorization": f"Bearer {token}"},
    )
    ids_activas = {c["id"] for c in resp_activas.json()}
    assert coh_activa["id"] in ids_activas
    assert coh_inactiva["id"] not in ids_activas


async def test_list_cohortes_filtro_q(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)
    carrera = await _create_carrera(client, token, "CAR-COH-Q")

    await _create_cohorte(client, token, carrera["id"], "2026 A")
    await _create_cohorte(client, token, carrera["id"], "2025 B")
    await _create_cohorte(client, token, carrera["id"], "2024 C")

    resp = await client.get(
        "/api/admin/cohortes?q=2026",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    nombres = {c["nombre"] for c in resp.json()}
    assert "2026 A" in nombres
    assert "2025 B" not in nombres


# ── Materias filters ──────────────────────────────────────────────────────


async def test_list_materias_filtro_activa(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    mat_activa = await _create_materia(client, token, "MAT-FLT-A", "Materia Activa F")
    mat_inactiva = await _create_materia(client, token, "MAT-FLT-I", "Materia Inactiva F")
    await client.put(
        f"/api/admin/materias/{mat_inactiva['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json={"estado": "Inactiva"},
    )

    resp_activas = await client.get(
        "/api/admin/materias?activa=true",
        headers={"Authorization": f"Bearer {token}"},
    )
    ids_activas = {m["id"] for m in resp_activas.json()}
    assert mat_activa["id"] in ids_activas
    assert mat_inactiva["id"] not in ids_activas


async def test_list_materias_filtro_q(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    await _create_materia(client, token, "MAT-ALG", "Álgebra Lineal")
    await _create_materia(client, token, "MAT-CAL", "Cálculo Diferencial")
    await _create_materia(client, token, "MAT-FIS", "Física I")

    resp = await client.get(
        "/api/admin/materias?q=Álgebra",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    nombres = {m["nombre"] for m in resp.json()}
    assert "Álgebra Lineal" in nombres
    assert "Cálculo Diferencial" not in nombres


async def test_list_materias_filtro_q_por_codigo(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    await _create_materia(client, token, "MAT-ALG")

    resp = await client.get(
        "/api/admin/materias?q=ALG",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert any(m["codigo"] == "MAT-ALG" for m in resp.json())


# ── Dictados filters ─────────────────────────────────────────────────────


async def test_list_dictados_filtro_activa(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)
    carrera = await _create_carrera(client, token, "CAR-DIC-FLT")
    materia = await _create_materia(client, token, "MAT-DIC-FLT")
    cohorte = await _create_cohorte(client, token, carrera["id"], "Coh Dictado F")

    dictado = await _create_dictado(client, token, materia["id"], carrera["id"], cohorte["id"])
    await client.patch(
        f"/api/admin/dictados/{dictado['id']}/estado",
        headers={"Authorization": f"Bearer {token}"},
    )

    resp_activos = await client.get(
        "/api/admin/dictados?activa=true",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_activos.status_code == 200
    assert dictado["id"] not in {d["id"] for d in resp_activos.json()}

    resp_inactivos = await client.get(
        "/api/admin/dictados?activa=false",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_inactivos.status_code == 200
    assert dictado["id"] in {d["id"] for d in resp_inactivos.json()}


async def test_list_dictados_filtro_vigente(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)
    carrera = await _create_carrera(client, token, "CAR-DIC-VIG")
    materia = await _create_materia(client, token, "MAT-DIC-VIG")
    cohorte_vig = await _create_cohorte(client, token, carrera["id"], "Coh Vigente")
    cohorte_venc = await _create_cohorte(client, token, carrera["id"], "Coh Vencida")

    today = date.today()
    yesterday = today - timedelta(days=1)
    last_year = today - timedelta(days=400)

    resp_vig = await client.post(
        "/api/admin/dictados",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "materia_id": materia["id"],
            "carrera_id": carrera["id"],
            "cohorte_id": cohorte_vig["id"],
            "vig_desde": yesterday.isoformat(),
            "vig_hasta": (today + timedelta(days=30)).isoformat(),
        },
    )
    assert resp_vig.status_code == 201
    dictado_vigente_id = resp_vig.json()["id"]

    resp_venc = await client.post(
        "/api/admin/dictados",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "materia_id": materia["id"],
            "carrera_id": carrera["id"],
            "cohorte_id": cohorte_venc["id"],
            "vig_desde": last_year.isoformat(),
            "vig_hasta": yesterday.isoformat(),
        },
    )
    assert resp_venc.status_code == 201

    resp = await client.get(
        "/api/admin/dictados?vigente=true",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    ids = {d["id"] for d in resp.json()}
    assert dictado_vigente_id in ids
    assert resp_venc.json()["id"] not in ids


async def test_list_dictados_filtro_q(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)
    carrera = await _create_carrera(client, token, "CAR-DIC-Q")
    materia = await _create_materia(client, token, "MAT-DIC-Q")
    cohorte = await _create_cohorte(client, token, carrera["id"], "Coh Dictado Q")

    await _create_dictado(client, token, materia["id"], carrera["id"], cohorte["id"])

    resp = await client.get(
        "/api/admin/dictados?q=Activo",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert len(resp.json()) >= 1
