from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import cleanup_permission_cache
from tests.test_evaluaciones.conftest import make_token


async def _create_carrera(client, token, codigo="CAR-EVAL"):
    resp = await client.post(
        "/api/admin/carreras",
        headers={"Authorization": f"Bearer {token}"},
        json={"codigo": codigo, "nombre": f"Carrera {codigo}"},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _create_materia(client, token, codigo="MAT-EVAL"):
    resp = await client.post(
        "/api/admin/materias",
        headers={"Authorization": f"Bearer {token}"},
        json={"codigo": codigo, "nombre": f"Materia {codigo}"},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _create_cohorte(client, token, carrera_id, nombre="Coh Evaluacion"):
    resp = await client.post(
        "/api/admin/cohortes",
        headers={"Authorization": f"Bearer {token}"},
        json={"carrera_id": carrera_id, "nombre": nombre, "anio": 2025},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


# ── POST / evaluaciones ───────────────────────────────────────────────────


async def test_create_evaluacion(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    carrera_id = await _create_carrera(client, token, "CAR-EVAL-1")
    materia_id = await _create_materia(client, token, "MAT-EVAL-1")
    cohorte_id = await _create_cohorte(client, token, carrera_id, "Coh Eval 1")

    resp = await client.post(
        "/api/v1/evaluaciones",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "materia_id": materia_id,
            "cohorte_id": cohorte_id,
            "tipo": "Parcial",
            "instancia": 1,
            "fecha": "2025-06-15",
            "titulo": "Primer Parcial",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["tipo"] == "Parcial"
    assert body["instancia"] == 1
    assert body["titulo"] == "Primer Parcial"
    assert body["materia_id"] == materia_id
    assert body["cohorte_id"] == cohorte_id


async def test_create_evaluacion_sin_cohorte(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    materia_id = await _create_materia(client, token, "MAT-EVAL-2")

    resp = await client.post(
        "/api/v1/evaluaciones",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "materia_id": materia_id,
            "tipo": "TP",
            "instancia": 1,
            "fecha": "2025-06-20",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["cohorte_id"] is None


async def test_create_evaluacion_sin_permiso_returns_403(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, alumno_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(alumno_user)

    resp = await client.post(
        "/api/v1/evaluaciones",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "materia_id": "00000000-0000-0000-0000-000000000000",
            "tipo": "Parcial",
            "instancia": 1,
            "fecha": "2025-06-15",
        },
    )
    assert resp.status_code == 403


# ── GET / evaluaciones ────────────────────────────────────────────────────


async def test_list_evaluaciones(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    carrera_id = await _create_carrera(client, token, "CAR-EVAL-3")
    materia_id = await _create_materia(client, token, "MAT-EVAL-3")
    cohorte_id = await _create_cohorte(client, token, carrera_id, "Coh Eval 3")

    await client.post(
        "/api/v1/evaluaciones",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "materia_id": materia_id,
            "cohorte_id": cohorte_id,
            "tipo": "Parcial",
            "instancia": 1,
            "fecha": "2025-06-15",
        },
    )
    await client.post(
        "/api/v1/evaluaciones",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "materia_id": materia_id,
            "cohorte_id": cohorte_id,
            "tipo": "Final",
            "instancia": 1,
            "fecha": "2025-07-01",
        },
    )

    resp = await client.get(
        "/api/v1/evaluaciones",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert len(resp.json()) >= 2


async def test_list_evaluaciones_filtro_materia(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    carrera_id = await _create_carrera(client, token, "CAR-EVAL-4")
    materia_a = await _create_materia(client, token, "MAT-EVAL-4A")
    materia_b = await _create_materia(client, token, "MAT-EVAL-4B")
    cohorte_id = await _create_cohorte(client, token, carrera_id, "Coh Eval 4")

    await client.post(
        "/api/v1/evaluaciones",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "materia_id": materia_a,
            "cohorte_id": cohorte_id,
            "tipo": "Parcial",
            "instancia": 1,
            "fecha": "2025-06-15",
        },
    )
    await client.post(
        "/api/v1/evaluaciones",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "materia_id": materia_b,
            "cohorte_id": cohorte_id,
            "tipo": "Parcial",
            "instancia": 1,
            "fecha": "2025-06-20",
        },
    )

    resp = await client.get(
        f"/api/v1/evaluaciones?materia_id={materia_a}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    evals = resp.json()
    assert all(e["materia_id"] == materia_a for e in evals)


# ── PUT / evaluaciones/{id} ───────────────────────────────────────────────


async def test_update_evaluacion(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    carrera_id = await _create_carrera(client, token, "CAR-EVAL-5")
    materia_id = await _create_materia(client, token, "MAT-EVAL-5")
    cohorte_id = await _create_cohorte(client, token, carrera_id, "Coh Eval 5")

    create_resp = await client.post(
        "/api/v1/evaluaciones",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "materia_id": materia_id,
            "cohorte_id": cohorte_id,
            "tipo": "Parcial",
            "instancia": 1,
            "fecha": "2025-06-15",
            "titulo": "Primer Parcial",
        },
    )
    evaluacion_id = create_resp.json()["id"]

    update_resp = await client.put(
        f"/api/v1/evaluaciones/{evaluacion_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "tipo": "Recuperatorio",
            "fecha": "2025-07-10",
        },
    )
    assert update_resp.status_code == 200
    body = update_resp.json()
    assert body["tipo"] == "Recuperatorio"
    assert body["fecha"] == "2025-07-10"
    assert body["instancia"] == 1


async def test_update_evaluacion_inexistente_returns_404(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    resp = await client.put(
        "/api/v1/evaluaciones/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {token}"},
        json={"tipo": "Final"},
    )
    assert resp.status_code == 404


# ── DELETE / evaluaciones/{id} ────────────────────────────────────────────


async def test_delete_evaluacion_soft_delete(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    carrera_id = await _create_carrera(client, token, "CAR-EVAL-6")
    materia_id = await _create_materia(client, token, "MAT-EVAL-6")
    cohorte_id = await _create_cohorte(client, token, carrera_id, "Coh Eval 6")

    create_resp = await client.post(
        "/api/v1/evaluaciones",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "materia_id": materia_id,
            "cohorte_id": cohorte_id,
            "tipo": "Parcial",
            "instancia": 1,
            "fecha": "2025-06-15",
        },
    )
    evaluacion_id = create_resp.json()["id"]

    delete_resp = await client.delete(
        f"/api/v1/evaluaciones/{evaluacion_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_resp.status_code == 200
    assert delete_resp.json()["deleted_at"] is True

    list_resp = await client.get(
        "/api/v1/evaluaciones",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert all(e["id"] != evaluacion_id for e in list_resp.json())


async def test_delete_evaluacion_inexistente_returns_404(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    resp = await client.delete(
        "/api/v1/evaluaciones/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404
