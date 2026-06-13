"""6.3: estructura:gestionar guard — ALUMNO -> 403, ADMIN -> OK, across
all entity groups (carreras/materias/cohortes/dictados)."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import cleanup_permission_cache
from tests.test_estructura.conftest import make_token

ENDPOINTS = [
    "/api/admin/carreras",
    "/api/admin/materias",
    "/api/admin/cohortes",
    "/api/admin/dictados",
]


@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_list_endpoint_forbidden_without_permission(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, alumno_user, endpoint
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(alumno_user)

    response = await client.get(endpoint, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_list_endpoint_allowed_for_admin(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, endpoint
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    response = await client.get(endpoint, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


async def test_endpoint_without_token_returns_401(client: AsyncClient):
    response = await client.get("/api/admin/carreras")
    assert response.status_code == 401
