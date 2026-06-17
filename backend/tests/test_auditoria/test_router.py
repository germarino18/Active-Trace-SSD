"""Integration tests for auditoria routers."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.models.audit_log import AuditLog
from app.models.comunicacion import Comunicacion
from app.models.materia import Materia
from app.models.tenant import Tenant
from app.repositories.base import BaseRepository
from app.schemas.auth import CurrentUser
from tests.helpers import cleanup_permission_cache, seed_permissions_for_tenant


@pytest.fixture
async def auth_user_no_perm(db_session, test_tenant) -> CurrentUser:
    from app.models.user import User
    from app.models.usuario import Usuario
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    user = await user_repo.create({
        "email": f"alumno-{uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "Alumno",
        "is_active": True,
    })
    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    await usuario_repo.create({
        "user_id": user.id,
        "nombre": "Alumno",
        "apellidos": "Test",
    })
    return CurrentUser(
        user_id=user.id,
        tenant_id=test_tenant.id,
        roles=["ALUMNO"],
    )


@pytest.mark.usefixtures("_setup_auth_admin")
class TestAuditoriaEndpointsAdmin:
    """ADMIN should have access to all endpoints."""

    async def test_get_acciones_por_dia(self, client: AsyncClient):
        resp = await client.get("/api/v1/auditoria/acciones-por-dia")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    async def test_get_comunicaciones_por_docente(self, client: AsyncClient):
        resp = await client.get("/api/v1/auditoria/comunicaciones-por-docente")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_get_interacciones_por_docente_materia(self, client: AsyncClient):
        resp = await client.get("/api/v1/auditoria/interacciones-por-docente-materia")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_get_ultimas_acciones(self, client: AsyncClient):
        resp = await client.get("/api/v1/auditoria/ultimas-acciones?limit=5")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "limit" in data

    async def test_get_log(self, client: AsyncClient):
        resp = await client.get("/api/v1/auditoria/log?offset=0&limit=10")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data

    async def test_log_pagination_validation(self, client: AsyncClient):
        """Negative offset should return 422."""
        resp = await client.get("/api/v1/auditoria/log?offset=-1&limit=10")
        assert resp.status_code == 422

    async def test_method_not_allowed(self, client: AsyncClient):
        """POST on auditoria endpoints should return 405."""
        resp = await client.post("/api/v1/auditoria/log")
        assert resp.status_code == 405


class TestAuditoriaEndpointsSinPermiso:
    """ALUMNO should get 403 on all endpoints."""

    @pytest.fixture(autouse=True)
    async def _override_auth(self, app, db_session, test_tenant, auth_user_no_perm):
        async def _override():
            return auth_user_no_perm
        app.dependency_overrides[get_current_user] = _override
        await seed_permissions_for_tenant(db_session, test_tenant.id)
        cleanup_permission_cache()
        yield
        app.dependency_overrides.pop(get_current_user, None)
        cleanup_permission_cache()

    async def test_acciones_por_dia_forbidden(self, client: AsyncClient):
        resp = await client.get("/api/v1/auditoria/acciones-por-dia")
        assert resp.status_code == 403

    async def test_log_forbidden(self, client: AsyncClient):
        resp = await client.get("/api/v1/auditoria/log")
        assert resp.status_code == 403

    async def test_ultimas_acciones_forbidden(self, client: AsyncClient):
        resp = await client.get("/api/v1/auditoria/ultimas-acciones")
        assert resp.status_code == 403


class TestAuditoriaLogDetalle:
    """Verify that the log endpoint returns data when entries exist."""

    @pytest.mark.usefixtures("_setup_auth_admin")
    async def test_returns_seeded_entry(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant: Tenant,
        test_materia: Materia,
        auth_admin: CurrentUser,
    ):
        from app.models.audit_log import AuditLog
        repo = BaseRepository(model=AuditLog, session=db_session, tenant_id=test_tenant.id)
        entry = await repo.create({
            "actor_id": auth_admin.user_id,  # Valid FK to users.id (created by auth_admin fixture)
            "materia_id": test_materia.id,
            "accion": "TEST_LOG",
            "detalle": {"key": "val"},
            "filas_afectadas": 1,
            "ip": "192.168.1.1",
            "user_agent": "test-agent",
        })
        resp = await client.get("/api/v1/auditoria/log?offset=0&limit=50")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        entry_id = str(entry.id)
        ids = [item["id"] for item in data["items"]]
        assert entry_id in ids
