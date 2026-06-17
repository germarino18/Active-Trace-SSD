"""Tests for perfil router."""
import pytest
from httpx import AsyncClient


class TestGetPerfil:
    async def test_get_perfil_returns_200(self, client: AsyncClient):
        response = await client.get("/api/v1/perfil")
        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Test"
        assert data["apellidos"] == "User"
        assert data["email"]
        assert "cuil" in data

    async def test_get_perfil_no_profile(
        self,
        client: AsyncClient,
        app,
        db_session,
        test_tenant,
        auth_user_no_profile,
    ):
        from app.api.dependencies.auth import get_current_user

        async def _override():
            return auth_user_no_profile

        app.dependency_overrides[get_current_user] = _override
        response = await client.get("/api/v1/perfil")
        assert response.status_code == 404


class TestUpdatePerfil:
    async def test_update_returns_200(self, client: AsyncClient):
        response = await client.patch(
            "/api/v1/perfil",
            json={"nombre": "Updated", "banco": "Nación"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Updated"
        assert data["banco"] == "Nación"

    async def test_cuil_rejected_422(self, client: AsyncClient):
        response = await client.patch(
            "/api/v1/perfil",
            json={"cuil": "20-12345678-9"},
        )
        assert response.status_code == 422

    async def test_empty_body_422(self, client: AsyncClient):
        response = await client.patch("/api/v1/perfil", json={})
        assert response.status_code == 422
