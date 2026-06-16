"""Integration tests for avisos router (C-15).

Uses client fixture with overridden get_current_user.
Seeds permissions so RBAC guards pass.
"""

from datetime import UTC, datetime
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.models.aviso import Aviso, AcknowledgmentAviso, AlcanceAviso, SeveridadAviso
from app.models.tenant import Tenant
from app.models.user import User
from app.models.usuario import Usuario
from app.repositories.base import BaseRepository
from app.schemas.auth import CurrentUser
from tests.helpers import cleanup_permission_cache, seed_permissions_for_tenant


_JAN2026 = datetime(2026, 1, 1, tzinfo=UTC)
_DEC2026 = datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC)


@pytest.fixture
async def auth_user(db_session, test_tenant) -> CurrentUser:
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    user = await user_repo.create({
        "email": f"coord-{uuid.uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "Coordinador",
        "is_active": True,
    })
    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    await usuario_repo.create({
        "user_id": user.id,
        "nombre": "Coord",
        "apellidos": "Test",
    })
    return CurrentUser(
        user_id=user.id,
        tenant_id=test_tenant.id,
        roles=["COORDINADOR"],
    )


@pytest.fixture
async def auth_usuario_id(db_session, auth_user, test_tenant) -> uuid.UUID:
    repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    usuarios = await repo.find_by(user_id=auth_user.user_id)
    if usuarios:
        return usuarios[0].id
    raise RuntimeError("Usuario not found for auth_user")


@pytest.fixture
async def auth_user_no_perm(db_session, test_tenant) -> CurrentUser:
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    user = await user_repo.create({
        "email": f"alumno-{uuid.uuid4().hex[:8]}@test.com",
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


@pytest.fixture(autouse=True)
async def _setup_auth(app, db_session, test_tenant, auth_user):
    async def _override_user():
        return auth_user

    app.dependency_overrides[get_current_user] = _override_user
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    cleanup_permission_cache()
    yield
    app.dependency_overrides.pop(get_current_user, None)
    cleanup_permission_cache()


async def _seed_aviso(
    db_session: AsyncSession, tenant_id: uuid.UUID, **overrides
) -> Aviso:
    repo = BaseRepository(model=Aviso, session=db_session, tenant_id=tenant_id)
    data = {
        "alcance": AlcanceAviso.GLOBAL.value,
        "severidad": SeveridadAviso.INFO.value,
        "titulo": "Aviso test",
        "cuerpo": "Cuerpo test",
        "inicio_en": _JAN2026,
        "fin_en": _DEC2026,
        "orden": 0,
        "activo": True,
        "requiere_ack": False,
    }
    data.update(overrides)
    return await repo.create(data)


# ── Create ──────────────────────────────────────────────────────────

class TestCreate:
    async def test_create_returns_201(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/avisos",
            json={
                "alcance": "GLOBAL",
                "titulo": "Nuevo aviso",
                "cuerpo": "Contenido del aviso",
                "inicio_en": _JAN2026.isoformat(),
                "fin_en": _DEC2026.isoformat(),
            },
        )
        assert response.status_code == 201
        body = response.json()
        assert body["titulo"] == "Nuevo aviso"
        assert body["alcance"] == "GLOBAL"

    async def test_create_with_all_fields(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/avisos",
            json={
                "alcance": "POR_ROL",
                "rol_destino": "ALUMNO",
                "severidad": "CRITICO",
                "titulo": "Aviso critico",
                "cuerpo": "Muy importante",
                "inicio_en": _JAN2026.isoformat(),
                "fin_en": _DEC2026.isoformat(),
                "orden": 5,
                "activo": True,
                "requiere_ack": True,
            },
        )
        assert response.status_code == 201

    async def test_create_invalid_returns_422(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/avisos",
            json={"alcance": "INVALIDO"},
        )
        assert response.status_code == 422

    async def test_create_without_perm_returns_403(
        self, client: AsyncClient, app, auth_user_no_perm,
    ):
        async def _override_user():
            return auth_user_no_perm
        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()

        response = await client.post(
            "/api/v1/avisos",
            json={
                "alcance": "GLOBAL",
                "titulo": "Test",
                "cuerpo": "Cuerpo",
                "inicio_en": _JAN2026.isoformat(),
                "fin_en": _DEC2026.isoformat(),
            },
        )
        assert response.status_code == 403


# ── Update ──────────────────────────────────────────────────────────

class TestUpdate:
    async def test_update_returns_200(
        self, client: AsyncClient, db_session, test_tenant,
    ):
        aviso = await _seed_aviso(db_session, test_tenant.id)
        response = await client.patch(
            f"/api/v1/avisos/{aviso.id}",
            json={"titulo": "Actualizado", "orden": 10},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["titulo"] == "Actualizado"

    async def test_update_not_found_returns_404(self, client: AsyncClient):
        response = await client.patch(
            f"/api/v1/avisos/{uuid.uuid4()}",
            json={"titulo": "Nope"},
        )
        assert response.status_code == 404

    async def test_update_without_perm_returns_403(
        self, client: AsyncClient, app, auth_user_no_perm,
    ):
        async def _override_user():
            return auth_user_no_perm
        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()

        response = await client.patch(
            f"/api/v1/avisos/{uuid.uuid4()}",
            json={"titulo": "Nope"},
        )
        assert response.status_code == 403


# ── Delete ──────────────────────────────────────────────────────────

class TestDelete:
    async def test_delete_returns_204(
        self, client: AsyncClient, db_session, test_tenant,
    ):
        aviso = await _seed_aviso(db_session, test_tenant.id)
        response = await client.delete(f"/api/v1/avisos/{aviso.id}")
        assert response.status_code == 204

    async def test_delete_not_found_returns_404(self, client: AsyncClient):
        response = await client.delete(f"/api/v1/avisos/{uuid.uuid4()}")
        assert response.status_code == 404

    async def test_delete_without_perm_returns_403(
        self, client: AsyncClient, app, auth_user_no_perm,
    ):
        async def _override_user():
            return auth_user_no_perm
        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()

        response = await client.delete(f"/api/v1/avisos/{uuid.uuid4()}")
        assert response.status_code == 403


# ── Get single ──────────────────────────────────────────────────────

class TestGet:
    async def test_get_returns_200(
        self, client: AsyncClient, db_session, test_tenant,
    ):
        aviso = await _seed_aviso(db_session, test_tenant.id)
        response = await client.get(f"/api/v1/avisos/{aviso.id}")
        assert response.status_code == 200
        body = response.json()
        assert body["id"] == str(aviso.id)

    async def test_get_not_found_returns_404(self, client: AsyncClient):
        response = await client.get(f"/api/v1/avisos/{uuid.uuid4()}")
        assert response.status_code == 404


# ── List managed ────────────────────────────────────────────────────

class TestList:
    async def test_list_returns_200(
        self, client: AsyncClient, db_session, test_tenant,
    ):
        await _seed_aviso(db_session, test_tenant.id, titulo="A1")
        await _seed_aviso(db_session, test_tenant.id, titulo="A2")
        response = await client.get("/api/v1/avisos")
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 2


# ── Visible ─────────────────────────────────────────────────────────

class TestVisible:
    async def test_visible_returns_200(self, client: AsyncClient, db_session, test_tenant):
        await _seed_aviso(db_session, test_tenant.id, titulo="Visible")
        response = await client.get("/api/v1/avisos/visible")
        assert response.status_code == 200
        body = response.json()
        titles = [a["titulo"] for a in body]
        assert "Visible" in titles

    async def test_visible_excludes_inactive(self, client: AsyncClient, db_session, test_tenant):
        await _seed_aviso(db_session, test_tenant.id, titulo="Inactivo", activo=False)
        response = await client.get("/api/v1/avisos/visible")
        assert response.status_code == 200
        body = response.json()
        assert all(a["activo"] is True for a in body)

    async def test_visible_without_auth_returns_401(self, client: AsyncClient, app):
        app.dependency_overrides.pop(get_current_user, None)
        response = await client.get("/api/v1/avisos/visible")
        assert response.status_code == 401


# ── Pendientes ──────────────────────────────────────────────────────

class TestPendientes:
    async def test_pendientes_returns_200(
        self, client: AsyncClient, db_session, test_tenant,
    ):
        await _seed_aviso(db_session, test_tenant.id, titulo="Pendiente", requiere_ack=True)
        response = await client.get("/api/v1/avisos/pendientes")
        assert response.status_code == 200
        body = response.json()
        assert len(body) >= 1

    async def test_pendientes_excludes_confirmed(
        self, client: AsyncClient, db_session, test_tenant, auth_usuario_id,
    ):
        a = await _seed_aviso(db_session, test_tenant.id, titulo="Confirmado", requiere_ack=True)
        ack_repo = BaseRepository(
            model=AcknowledgmentAviso,
            session=db_session,
            tenant_id=test_tenant.id,
        )
        await ack_repo.create({"aviso_id": a.id, "usuario_id": auth_usuario_id})
        response = await client.get("/api/v1/avisos/pendientes")
        assert response.status_code == 200
        body = response.json()
        assert all(a["titulo"] != "Confirmado" for a in body)

    async def test_pendientes_without_auth_returns_401(self, client: AsyncClient, app):
        app.dependency_overrides.pop(get_current_user, None)
        response = await client.get("/api/v1/avisos/pendientes")
        assert response.status_code == 401


# ── Confirmar ───────────────────────────────────────────────────────

class TestConfirmar:
    async def test_confirmar_returns_200(
        self, client: AsyncClient, db_session, test_tenant,
    ):
        a = await _seed_aviso(db_session, test_tenant.id, requiere_ack=True)
        response = await client.post(f"/api/v1/avisos/{a.id}/confirmar")
        assert response.status_code == 200
        body = response.json()
        assert body["acknowledged"] is True

    async def test_confirmar_idempotent(
        self, client: AsyncClient, db_session, test_tenant, auth_usuario_id,
    ):
        a = await _seed_aviso(db_session, test_tenant.id, requiere_ack=True)
        r1 = await client.post(f"/api/v1/avisos/{a.id}/confirmar")
        assert r1.status_code == 200
        r2 = await client.post(f"/api/v1/avisos/{a.id}/confirmar")
        assert r2.status_code == 200
        assert r2.json()["acknowledged"] is True

    async def test_confirmar_not_found_returns_404(self, client: AsyncClient):
        response = await client.post(f"/api/v1/avisos/{uuid.uuid4()}/confirmar")
        assert response.status_code == 404

    async def test_confirmar_without_perm_returns_403(
        self, client: AsyncClient, app, db_session, test_tenant,
    ):
        user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
        user = await user_repo.create({
            "email": f"nexo-{uuid.uuid4().hex[:8]}@test.com",
            "password_hash": "hash",
            "display_name": "Nexo",
            "is_active": True,
        })
        usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
        await usuario_repo.create({
            "user_id": user.id,
            "nombre": "Nexo",
            "apellidos": "Test",
        })
        no_perm_user = CurrentUser(
            user_id=user.id,
            tenant_id=test_tenant.id,
            roles=["NEXO"],
        )
        async def _override_user():
            return no_perm_user
        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()

        response = await client.post(
            f"/api/v1/avisos/{uuid.uuid4()}/confirmar"
        )
        assert response.status_code == 403

    async def test_confirmar_without_auth_returns_401(self, client: AsyncClient, app):
        app.dependency_overrides.pop(get_current_user, None)
        response = await client.post(f"/api/v1/avisos/{uuid.uuid4()}/confirmar")
        assert response.status_code == 401


# ── Stats ───────────────────────────────────────────────────────────

class TestStats:
    async def test_stats_returns_200(
        self, client: AsyncClient, db_session, test_tenant,
    ):
        a = await _seed_aviso(db_session, test_tenant.id, requiere_ack=True)
        response = await client.get(f"/api/v1/avisos/{a.id}/stats")
        assert response.status_code == 200
        body = response.json()
        assert "total" in body

    async def test_stats_not_found_returns_404(self, client: AsyncClient):
        response = await client.get(f"/api/v1/avisos/{uuid.uuid4()}/stats")
        assert response.status_code == 404

    async def test_stats_without_perm_returns_403(
        self, client: AsyncClient, app, auth_user_no_perm,
    ):
        async def _override_user():
            return auth_user_no_perm
        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()

        response = await client.get(f"/api/v1/avisos/{uuid.uuid4()}/stats")
        assert response.status_code == 403
