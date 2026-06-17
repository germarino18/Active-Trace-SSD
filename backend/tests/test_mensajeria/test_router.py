"""Tests for inbox router."""
import pytest
from httpx import AsyncClient


class TestListHilos:
    async def test_list_hilos_returns_200(self, client: AsyncClient, test_hilo):
        response = await client.get("/api/v1/inbox/hilos")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["asunto"] == "Test conversation"

    async def test_list_hilos_unauthorized(self, client: AsyncClient, app):
        """Sin auth, da 401."""
        from app.api.dependencies.auth import get_current_user
        app.dependency_overrides.pop(get_current_user, None)
        response = await client.get("/api/v1/inbox/hilos")
        assert response.status_code == 401


class TestGetHilo:
    async def test_get_hilo_returns_200(self, client: AsyncClient, test_hilo):
        response = await client.get(f"/api/v1/inbox/hilos/{test_hilo.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert "Hola" in data[0]["contenido"]

    async def test_get_hilo_nonexistent_404(self, client: AsyncClient):
        from uuid import uuid4
        response = await client.get(f"/api/v1/inbox/hilos/{uuid4()}")
        assert response.status_code == 404


class TestResponder:
    async def test_responder_returns_201(self, client: AsyncClient, test_hilo):
        response = await client.post(
            f"/api/v1/inbox/hilos/{test_hilo.id}/responder",
            json={"contenido": "Gracias!"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["contenido"] == "Gracias!"

    async def test_responder_empty_422(self, client: AsyncClient, test_hilo):
        response = await client.post(
            f"/api/v1/inbox/hilos/{test_hilo.id}/responder",
            json={"contenido": ""},
        )
        assert response.status_code == 422

    async def test_responder_nonexistent_hilo_404(self, client: AsyncClient):
        from uuid import uuid4
        response = await client.post(
            f"/api/v1/inbox/hilos/{uuid4()}/responder",
            json={"contenido": "Hola"},
        )
        assert response.status_code == 404
