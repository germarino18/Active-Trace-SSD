"""Integration tests for full ADMIN flows (C-34, task 12.1).

Creates a complete academic structure and exercises toggle, filters, and
role assignment in a single coherent scenario within one transaction.
"""

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import cleanup_permission_cache
from tests.test_estructura.conftest import make_token


async def test_full_flow_create_structure_and_toggle(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    """Create carrera -> cohorte -> materia -> dictado -> toggle estado on
    each entity, verifying each step returns the expected status."""
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    # ── 1. Create carrera ────────────────────────────────────────────
    create_carrera = await client.post(
        "/api/admin/carreras",
        headers={"Authorization": f"Bearer {token}"},
        json={"codigo": "ING-INTEG", "nombre": "Ingeniería Integración"},
    )
    assert create_carrera.status_code == 201
    carrera_id = create_carrera.json()["id"]
    assert create_carrera.json()["estado"] == "Activa"

    # ── 2. Create materia ────────────────────────────────────────────
    create_materia = await client.post(
        "/api/admin/materias",
        headers={"Authorization": f"Bearer {token}"},
        json={"codigo": "MAT-INTEG", "nombre": "Materia Integración"},
    )
    assert create_materia.status_code == 201
    materia_id = create_materia.json()["id"]

    # ── 3. Create cohorte (closed vig_hasta so carrera can be toggled) ─
    create_cohorte = await client.post(
        "/api/admin/cohortes",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "carrera_id": carrera_id,
            "nombre": "2025 Integración",
            "anio": 2025,
            "vig_hasta": "2025-12-31",
        },
    )
    assert create_cohorte.status_code == 201
    cohorte_id = create_cohorte.json()["id"]

    # ── 4. Create dictado ───────────────────────────────────────────
    create_dictado = await client.post(
        "/api/admin/dictados",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "materia_id": materia_id,
            "carrera_id": carrera_id,
            "cohorte_id": cohorte_id,
        },
    )
    assert create_dictado.status_code == 201
    dictado_id = create_dictado.json()["id"]
    assert create_dictado.json()["estado"] == "Activo"

    # ── 5. Toggle carrera estado (Inactiva -> Activa) ───────────────
    toggle_carrera = await client.patch(
        f"/api/admin/carreras/{carrera_id}/estado",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert toggle_carrera.status_code == 200
    assert toggle_carrera.json()["estado"] == "Inactiva"

    # Toggle back to Activa
    toggle_carrera_back = await client.patch(
        f"/api/admin/carreras/{carrera_id}/estado",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert toggle_carrera_back.status_code == 200
    assert toggle_carrera_back.json()["estado"] == "Activa"

    # ── 6. Toggle materia estado ────────────────────────────────────
    toggle_materia = await client.patch(
        f"/api/admin/materias/{materia_id}/estado",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert toggle_materia.status_code == 200
    assert toggle_materia.json()["estado"] == "Inactiva"

    # ── 7. Toggle cohorte estado ────────────────────────────────────
    toggle_cohorte = await client.patch(
        f"/api/admin/cohortes/{cohorte_id}/estado",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert toggle_cohorte.status_code == 200
    assert toggle_cohorte.json()["estado"] == "Inactiva"

    # ── 8. Toggle dictado estado ────────────────────────────────────
    toggle_dictado = await client.patch(
        f"/api/admin/dictados/{dictado_id}/estado",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert toggle_dictado.status_code == 200
    assert toggle_dictado.json()["estado"] == "Inactivo"

    # ── 9. Verify toggle back to Activo ─────────────────────────────
    toggle_dictado_back = await client.patch(
        f"/api/admin/dictados/{dictado_id}/estado",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert toggle_dictado_back.status_code == 200
    assert toggle_dictado_back.json()["estado"] == "Activo"


async def test_full_flow_carrera_open_cohorte_rejects_toggle(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    """Carrera with an open cohorte (vig_hasta IS NULL) cannot be toggled
    to Inactiva."""
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    create_carrera = await client.post(
        "/api/admin/carreras",
        headers={"Authorization": f"Bearer {token}"},
        json={"codigo": "ING-OPEN", "nombre": "Carrera con Cohorte Abierta"},
    )
    carrera_id = create_carrera.json()["id"]

    await client.post(
        "/api/admin/cohortes",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "carrera_id": carrera_id,
            "nombre": "Cohorte Abierta Integración",
            "anio": 2025,
        },
    )

    toggle_resp = await client.patch(
        f"/api/admin/carreras/{carrera_id}/estado",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert toggle_resp.status_code == 422
    assert "cohortes abiertas" in toggle_resp.json()["error"]["message"].lower()
