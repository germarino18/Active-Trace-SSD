from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import cleanup_permission_cache
from tests.test_fechas_academicas.conftest import make_token


@pytest.mark.asyncio
async def test_create_fecha_returns_201(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, seeded_dictado
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    resp = await client.post(
        "/api/v1/fechas-academicas",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "dictado_id": str(seeded_dictado),
            "tipo": "Parcial",
            "numero": 1,
            "periodo": "2026-1",
            "fecha": "2026-04-15T10:00:00Z",
            "titulo": "Primer Parcial",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["titulo"] == "Primer Parcial"
    assert body["tipo"] == "Parcial"
    assert body["numero"] == 1
    assert body["periodo"] == "2026-1"
    assert "id" in body


@pytest.mark.asyncio
async def test_create_fecha_duplicate_returns_422(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, seeded_dictado
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    payload = {
        "dictado_id": str(seeded_dictado),
        "tipo": "TP",
        "numero": 1,
        "periodo": "2026-1",
        "fecha": "2026-05-01T10:00:00Z",
        "titulo": "TP 1",
    }
    first = await client.post(
        "/api/v1/fechas-academicas",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    assert first.status_code == 201

    second = await client.post(
        "/api/v1/fechas-academicas",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    assert second.status_code == 422


@pytest.mark.asyncio
async def test_get_fecha_returns_200(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, seeded_dictado
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    create = await client.post(
        "/api/v1/fechas-academicas",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "dictado_id": str(seeded_dictado),
            "tipo": "Parcial", "numero": 1,
            "periodo": "2026-1", "fecha": "2026-04-15T10:00:00Z",
            "titulo": "P1",
        },
    )
    assert create.status_code == 201
    fecha_id = create.json()["id"]

    get = await client.get(
        f"/api/v1/fechas-academicas/{fecha_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get.status_code == 200
    assert get.json()["id"] == fecha_id


@pytest.mark.asyncio
async def test_list_fechas_returns_200(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, seeded_dictado
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    await client.post(
        "/api/v1/fechas-academicas",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "dictado_id": str(seeded_dictado),
            "tipo": "Parcial", "numero": 1,
            "periodo": "2026-1", "fecha": "2026-04-15T10:00:00Z",
            "titulo": "P1",
        },
    )

    list_resp = await client.get(
        "/api/v1/fechas-academicas",
        headers={"Authorization": f"Bearer {token}"},
        params={"dictado_id": str(seeded_dictado), "periodo": "2026-1"},
    )
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1


@pytest.mark.asyncio
async def test_delete_fecha_returns_204(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, seeded_dictado
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    create = await client.post(
        "/api/v1/fechas-academicas",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "dictado_id": str(seeded_dictado),
            "tipo": "Coloquio", "numero": 1,
            "periodo": "2026-1", "fecha": "2026-06-01T10:00:00Z",
            "titulo": "Coloquio",
        },
    )
    assert create.status_code == 201
    fecha_id = create.json()["id"]

    delete = await client.delete(
        f"/api/v1/fechas-academicas/{fecha_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete.status_code == 204

    get = await client.get(
        f"/api/v1/fechas-academicas/{fecha_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get.status_code == 404


@pytest.mark.asyncio
async def test_calendario_returns_grouped(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, seeded_dictado
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    await client.post(
        "/api/v1/fechas-academicas",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "dictado_id": str(seeded_dictado),
            "tipo": "Parcial", "numero": 1,
            "periodo": "2026-1", "fecha": "2026-04-15T10:00:00Z",
            "titulo": "P1",
        },
    )

    cal = await client.get(
        "/api/v1/fechas-academicas/calendario",
        headers={"Authorization": f"Bearer {token}"},
        params={"dictado_id": str(seeded_dictado), "periodo": "2026-1"},
    )
    assert cal.status_code == 200
    data = cal.json()
    assert "2026-04" in data
    assert len(data["2026-04"]) == 1


@pytest.mark.asyncio
async def test_fragmento_lms_returns_content(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, seeded_dictado
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    await client.post(
        "/api/v1/fechas-academicas",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "dictado_id": str(seeded_dictado),
            "tipo": "Parcial", "numero": 1,
            "periodo": "2026-1", "fecha": "2026-04-15T10:00:00Z",
            "titulo": "P1",
        },
    )

    frag = await client.get(
        "/api/v1/fechas-academicas/fragmento-lms",
        headers={"Authorization": f"Bearer {token}"},
        params={"dictado_id": str(seeded_dictado), "periodo": "2026-1"},
    )
    assert frag.status_code == 200
    assert "Cronograma" in frag.json()["contenido"]


@pytest.mark.asyncio
async def test_fechas_without_permission_returns_403(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, alumno_user, seeded_dictado
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(alumno_user)

    resp = await client.post(
        "/api/v1/fechas-academicas",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "dictado_id": str(seeded_dictado),
            "tipo": "Parcial", "numero": 1,
            "periodo": "2026-1", "fecha": "2026-04-15T10:00:00Z",
            "titulo": "No Perm",
        },
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_fechas_other_tenant_returns_404(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, another_tenant_admin
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(another_tenant_admin)

    get = await client.get(
        f"/api/v1/fechas-academicas/{uuid4()}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get.status_code == 404
