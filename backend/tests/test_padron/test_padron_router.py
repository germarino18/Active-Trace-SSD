"""Integration tests for padrón router (Task 7.3).

Uses the `client` fixture with overridden get_current_user to bypass
auth. Seeds permissions so RBAC guards pass for the test user.
Tests cover: successful requests, permission errors, payload validation.
"""

import csv
import io
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.repositories.base import BaseRepository
from app.models.user import User
from app.schemas.auth import CurrentUser
from tests.helpers import cleanup_permission_cache, seed_permissions_for_tenant


def _make_csv_bytes(rows: list[dict]) -> bytes:
    if not rows:
        return b""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


@pytest.fixture
async def auth_user(db_session, test_tenant) -> CurrentUser:
    """Create a real User + seed permissions, return CurrentUser."""
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    user = await user_repo.create({
        "email": f"admin-{uuid.uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "Admin",
        "is_active": True,
        "roles": ["ADMIN"],
    })
    return CurrentUser(
        user_id=user.id,
        tenant_id=test_tenant.id,
        roles=["ADMIN"],
    )


@pytest.fixture
async def auth_user_no_perm(db_session, test_tenant) -> CurrentUser:
    """User with ALUMNO role (no PADRON permissions)."""
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    user = await user_repo.create({
        "email": f"alumno-{uuid.uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "Alumno",
        "is_active": True,
        "roles": ["ALUMNO"],
    })
    return CurrentUser(
        user_id=user.id,
        tenant_id=test_tenant.id,
        roles=["ALUMNO"],
    )


@pytest.fixture(autouse=True)
async def _setup_auth(app, db_session, test_tenant, auth_user):
    """Override auth dependency and seed permissions for every test."""
    async def _override_user():
        return auth_user

    app.dependency_overrides[get_current_user] = _override_user
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    cleanup_permission_cache()
    yield
    app.dependency_overrides.pop(get_current_user, None)
    cleanup_permission_cache()


class TestPreview:
    async def test_preview_with_valid_csv_returns_200(self, client: AsyncClient):
        csv_content = _make_csv_bytes([
            {"nombre": "Juan", "apellidos": "Pérez", "email": "juan@test.com", "comision": "A"},
        ])

        response = await client.post(
            "/api/admin/padron/preview",
            files={"file": ("alumnos.csv", csv_content, "text/csv")},
            data={"dictado_id": str(uuid.uuid4())},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_filas"] == 1
        assert "preview_token" in data
        assert "columnas_encontradas" in data

    async def test_preview_without_perm_returns_403(
        self, client: AsyncClient, app, auth_user_no_perm
    ):
        async def _override_user():
            return auth_user_no_perm

        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()

        csv_content = _make_csv_bytes([
            {"nombre": "Juan", "apellidos": "Pérez", "email": "juan@test.com"},
        ])

        response = await client.post(
            "/api/admin/padron/preview",
            files={"file": ("alumnos.csv", csv_content, "text/csv")},
            data={"dictado_id": str(uuid.uuid4())},
        )

        assert response.status_code == 403


class TestImportar:
    async def test_importar_with_invalid_token_returns_422(self, client: AsyncClient):
        response = await client.post(
            "/api/admin/padron/importar",
            json={
                "dictado_id": str(uuid.uuid4()),
                "preview_token": "invalid-token",
            },
        )

        assert response.status_code == 422

    async def test_importar_without_perm_returns_403(
        self, client: AsyncClient, app, auth_user_no_perm
    ):
        async def _override_user():
            return auth_user_no_perm

        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()

        response = await client.post(
            "/api/admin/padron/importar",
            json={
                "dictado_id": str(uuid.uuid4()),
                "preview_token": "some-token",
            },
        )

        assert response.status_code == 403


class TestObtenerPadron:
    async def test_get_padron_returns_200_with_empty_list(self, client: AsyncClient):
        response = await client.get(
            f"/api/admin/padron/dictados/{uuid.uuid4()}",
        )

        assert response.status_code == 200
        data = response.json()
        assert data == []

    async def test_get_padron_without_perm_returns_403(
        self, client: AsyncClient, app, auth_user_no_perm
    ):
        async def _override_user():
            return auth_user_no_perm

        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()

        response = await client.get(
            f"/api/admin/padron/dictados/{uuid.uuid4()}",
        )

        assert response.status_code == 403


class TestVersiones:
    async def test_versiones_returns_200(self, client: AsyncClient):
        response = await client.get(
            "/api/admin/padron/versiones",
            params={"dictado_id": str(uuid.uuid4())},
        )

        assert response.status_code == 200
        data = response.json()
        assert "versiones" in data
        assert data["versiones"] == []


class TestVaciar:
    async def test_vaciar_without_perm_returns_403(
        self, client: AsyncClient, app, auth_user_no_perm
    ):
        async def _override_user():
            return auth_user_no_perm

        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()

        response = await client.post(
            f"/api/admin/padron/dictados/{uuid.uuid4()}/vaciar",
        )

        assert response.status_code == 403


class TestSyncMoodle:
    async def test_sync_moodle_with_invalid_config_returns_502(self, client: AsyncClient):
        response = await client.post(
            "/api/admin/padron/sync/moodle",
            json={
                "dictado_id": str(uuid.uuid4()),
                "base_url": "https://moodle.invalid",
                "token": "bad-token",
                "course_id": 1,
            },
        )

        assert response.status_code == 502

    async def test_sync_moodle_without_perm_returns_403(
        self, client: AsyncClient, app, auth_user_no_perm
    ):
        async def _override_user():
            return auth_user_no_perm

        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()

        response = await client.post(
            "/api/admin/padron/sync/moodle",
            json={
                "dictado_id": str(uuid.uuid4()),
                "base_url": "https://moodle.test",
                "token": "tok",
                "course_id": 1,
            },
        )

        assert response.status_code == 403
