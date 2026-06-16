"""Integration tests for coloquios API endpoints."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from tests.helpers import cleanup_permission_cache
from tests.test_coloquios.conftest import make_token, _make_dictado

_URL_PREFIX = "/api/v1/coloquios"


# ── Helpers ─────────────────────────────────────────────────────────────────


async def _crear_evaluacion_payload(client, token, dictado_id):
    """Helper: create an evaluacion and return it."""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "dictado_id": str(dictado_id),
        "tipo": "Coloquio",
        "instancia": "Coloquio Test",
        "dias_disponibles": 10,
        "cupo_maximo": 30,
    }
    resp = await client.post(_URL_PREFIX, json=payload, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


async def _convocar_alumno(client, token, evaluacion_id, alumno_user):
    """Helper: import an alumno to evaluacion."""
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.post(
        f"{_URL_PREFIX}/{evaluacion_id}/importar-alumnos",
        json={"alumno_ids": [str(alumno_user.id)]},
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


# ── Tests ───────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_crear_evaluacion_201(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_tenant,
    coordinador_user,
    dictado_valido,
):
    """Creating an evaluacion should return 201."""
    await db_session.commit()
    cleanup_permission_cache()
    token = make_token(coordinador_user)
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "dictado_id": str(dictado_valido.id),
        "tipo": "Coloquio",
        "instancia": "Coloquio Final Diciembre 2026",
        "dias_disponibles": 15,
        "cupo_maximo": 25,
    }

    response = await client.post(_URL_PREFIX, json=payload, headers=headers)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["instancia"] == "Coloquio Final Diciembre 2026"
    assert data["cupo_maximo"] == 25
    assert data["estado"] == "Activa"


@pytest.mark.asyncio
async def test_crear_evaluacion_sin_permiso_403(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_tenant,
    alumno_user,
):
    """User without coloquios:gestionar should get 403."""
    await db_session.commit()
    cleanup_permission_cache()
    token = make_token(alumno_user)
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "dictado_id": "00000000-0000-0000-0000-000000000001",
        "tipo": "Coloquio",
        "instancia": "Test",
        "cupo_maximo": 10,
    }

    response = await client.post(_URL_PREFIX, json=payload, headers=headers)
    assert response.status_code == 403, response.text


@pytest.mark.asyncio
async def test_listar_evaluaciones_200(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_tenant,
    profesor_user,
    dictado_valido,
):
    """Listing evaluaciones should return 200."""
    await db_session.commit()
    cleanup_permission_cache()
    token = make_token(profesor_user)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(_URL_PREFIX, headers=headers)
    assert response.status_code == 200, response.text
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_cerrar_evaluacion(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_tenant,
    coordinador_user,
    dictado_valido,
):
    """Closing an evaluacion should set estado to Cerrada."""
    await db_session.commit()
    cleanup_permission_cache()
    token = make_token(coordinador_user)

    # Create first
    ev = await _crear_evaluacion_payload(client, token, dictado_valido.id)

    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.post(
        f"{_URL_PREFIX}/{ev['id']}/cerrar", headers=headers
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["estado"] == "Cerrada"


@pytest.mark.asyncio
async def test_importar_alumnos(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_tenant,
    coordinador_user,
    alumno_user,
    dictado_valido,
):
    """Importing alumnos to an evaluacion should work."""
    await db_session.commit()
    cleanup_permission_cache()
    token = make_token(coordinador_user)
    ev = await _crear_evaluacion_payload(client, token, dictado_valido.id)

    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.post(
        f"{_URL_PREFIX}/{ev['id']}/importar-alumnos",
        json={"alumno_ids": [str(alumno_user.id)]},
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["importados"] == 1

    # Idempotent — second import should say 0
    resp2 = await client.post(
        f"{_URL_PREFIX}/{ev['id']}/importar-alumnos",
        json={"alumno_ids": [str(alumno_user.id)]},
        headers=headers,
    )
    assert resp2.status_code == 200, resp2.text
    assert resp2.json()["importados"] == 0


@pytest.mark.asyncio
async def test_reservar_turno(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_tenant,
    coordinador_user,
    alumno_user,
    dictado_valido,
):
    """ALUMNO with coloquios:reservar should be able to reserve."""
    await db_session.commit()
    cleanup_permission_cache()

    coord_token = make_token(coordinador_user)
    ev = await _crear_evaluacion_payload(client, coord_token, dictado_valido.id)

    # Convocar alumno first
    await _convocar_alumno(client, coord_token, ev["id"], alumno_user)

    # Now reserve as alumno
    alumno_token = make_token(alumno_user)
    headers = {"Authorization": f"Bearer {alumno_token}"}
    resp = await client.post(
        f"{_URL_PREFIX}/{ev['id']}/reservar", headers=headers
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["estado"] == "Activa"
    assert data["alumno_id"] == str(alumno_user.id)


@pytest.mark.asyncio
async def test_reservar_sin_permiso_403(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_tenant,
    profesor_user,
    dictado_valido,
):
    """User without coloquios:reservar should get 403."""
    await db_session.commit()
    cleanup_permission_cache()
    token = make_token(profesor_user)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post(
        f"{_URL_PREFIX}/{uuid.uuid4()}/reservar", headers=headers
    )
    assert resp.status_code == 403, resp.text


@pytest.mark.asyncio
async def test_cancelar_reserva(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_tenant,
    coordinador_user,
    alumno_user,
    dictado_valido,
):
    """Owner can cancel their reservation."""
    await db_session.commit()
    cleanup_permission_cache()

    coord_token = make_token(coordinador_user)
    ev = await _crear_evaluacion_payload(client, coord_token, dictado_valido.id)
    await _convocar_alumno(client, coord_token, ev["id"], alumno_user)

    # Reserve as alumno
    alumno_token = make_token(alumno_user)
    headers = {"Authorization": f"Bearer {alumno_token}"}
    resp = await client.post(
        f"{_URL_PREFIX}/{ev['id']}/reservar", headers=headers
    )
    assert resp.status_code == 200, resp.text
    reserva = resp.json()

    # Cancel as alumno
    resp_cancel = await client.post(
        f"{_URL_PREFIX}/reservas/{reserva['id']}/cancelar",
        headers=headers,
    )
    assert resp_cancel.status_code == 200, resp_cancel.text
    assert resp_cancel.json()["estado"] == "Cancelada"


@pytest.mark.asyncio
async def test_registrar_resultado(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_tenant,
    coordinador_user,
    alumno_user,
    dictado_valido,
):
    """Registering a result for a convocado alumno should work."""
    await db_session.commit()
    cleanup_permission_cache()

    coord_token = make_token(coordinador_user)
    ev = await _crear_evaluacion_payload(client, coord_token, dictado_valido.id)
    await _convocar_alumno(client, coord_token, ev["id"], alumno_user)

    headers = {"Authorization": f"Bearer {coord_token}"}
    resp = await client.post(
        f"{_URL_PREFIX}/{ev['id']}/resultados",
        json={
            "evaluacion_id": ev["id"],
            "alumno_id": str(alumno_user.id),
            "nota_final": "Aprobado (8)",
        },
        headers=headers,
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["nota_final"] == "Aprobado (8)"


@pytest.mark.asyncio
async def test_registro_academico(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_tenant,
    coordinador_user,
    alumno_user,
    profesor_user,
    dictado_valido,
):
    """Getting academic record should return results."""
    await db_session.commit()
    cleanup_permission_cache()

    coord_token = make_token(coordinador_user)
    ev = await _crear_evaluacion_payload(client, coord_token, dictado_valido.id)
    await _convocar_alumno(client, coord_token, ev["id"], alumno_user)

    # Register result
    headers = {"Authorization": f"Bearer {coord_token}"}
    await client.post(
        f"{_URL_PREFIX}/{ev['id']}/resultados",
        json={
            "evaluacion_id": ev["id"],
            "alumno_id": str(alumno_user.id),
            "nota_final": "9",
        },
        headers=headers,
    )

    # Read using coloquios:ver (profesor has that)
    prof_token = make_token(profesor_user)
    prof_headers = {"Authorization": f"Bearer {prof_token}"}

    resp = await client.get(
        f"{_URL_PREFIX}/resultados",
        headers=prof_headers,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_listar_reservas_ver_permiso_200(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_tenant,
    profesor_user,
    dictado_valido,
):
    """User with coloquios:ver can list agenda."""
    await db_session.commit()
    cleanup_permission_cache()
    token = make_token(profesor_user)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get(f"{_URL_PREFIX}/reservas", headers=headers)
    assert resp.status_code == 200, resp.text
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_ver_metricas_200(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_tenant,
    profesor_user,
):
    """User with coloquios:ver can access metricas."""
    await db_session.commit()
    cleanup_permission_cache()
    token = make_token(profesor_user)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get(f"{_URL_PREFIX}/metricas", headers=headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "instancias_activas" in data
    assert "reservas_activas" in data


@pytest.mark.asyncio
async def test_multi_tenant_isolation(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_tenant,
    another_tenant,
    coordinador_user,
    alumno_user,
    dictado_valido,
):
    """Data from tenant 1 should not be visible from tenant 2."""
    await db_session.commit()
    cleanup_permission_cache()

    # Seed permissions for tenant 2
    from tests.helpers import seed_permissions_for_tenant
    await seed_permissions_for_tenant(db_session, another_tenant.id)

    # Create evaluacion in tenant 1
    coord_token = make_token(coordinador_user)
    await _crear_evaluacion_payload(client, coord_token, dictado_valido.id)

    # Create a user for tenant 2 and try to list
    from tests.test_coloquios.conftest import _make_user
    otro_admin = await _make_user(
        db_session, another_tenant.id, "admin2@coloquios.test", ["ADMIN"]
    )
    await db_session.commit()
    cleanup_permission_cache()

    otro_token = make_token(otro_admin)
    headers = {"Authorization": f"Bearer {otro_token}"}
    resp = await client.get(_URL_PREFIX, headers=headers)
    assert resp.status_code == 200, resp.text
    # Tenant 2 should see 0 evaluaciones
    assert len(resp.json()) == 0
