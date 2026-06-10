from httpx import AsyncClient


async def test_health_returns_200_and_status(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"


async def test_health_includes_database_field(client: AsyncClient):
    response = await client.get("/health")
    data = response.json()
    assert "database" in data


async def test_health_database_up_when_connected(client: AsyncClient):
    response = await client.get("/health")
    data = response.json()
    assert data["database"] == "up"
