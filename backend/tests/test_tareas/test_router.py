"""Integration tests for tareas router (C-16)."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.models.tarea import Tarea, TareaEstado
from app.models.tenant import Tenant
from app.models.user import User
from app.models.usuario import Usuario
from app.repositories.base import BaseRepository
from app.schemas.auth import CurrentUser
from tests.helpers import cleanup_permission_cache, seed_permissions_for_tenant


@pytest.fixture
async def coord_user(db_session, test_tenant) -> User:
    repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({
        "email": f"coord-{uuid.uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "Coordinador",
        "is_active": True,
    })


@pytest.fixture
async def coord_usuario(db_session, test_tenant, coord_user) -> Usuario:
    repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    u = await repo.create({"user_id": coord_user.id, "nombre": "Coord", "apellidos": "Test"})
    return u


@pytest.fixture
async def auth_user(coord_user, test_tenant) -> CurrentUser:
    return CurrentUser(user_id=coord_user.id, tenant_id=test_tenant.id, roles=["COORDINADOR"])


@pytest.fixture
async def prof_user(db_session, test_tenant) -> User:
    repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({
        "email": f"prof-{uuid.uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "Profesor",
        "is_active": True,
    })


@pytest.fixture
async def prof_usuario(db_session, test_tenant, prof_user) -> Usuario:
    repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({"user_id": prof_user.id, "nombre": "Prof", "apellidos": "Test"})


@pytest.fixture
async def auth_prof_user(prof_user, test_tenant) -> CurrentUser:
    return CurrentUser(user_id=prof_user.id, tenant_id=test_tenant.id, roles=["PROFESOR"])


@pytest.fixture(autouse=True)
async def _setup_auth(app, db_session, test_tenant, auth_user, coord_usuario):
    async def _override_user():
        return auth_user
    app.dependency_overrides[get_current_user] = _override_user
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    cleanup_permission_cache()
    yield
    app.dependency_overrides.pop(get_current_user, None)
    cleanup_permission_cache()


async def _make_usuario(db_session: AsyncSession, tenant_id: uuid.UUID) -> Usuario:
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=tenant_id)
    user = await user_repo.create({
        "email": f"tarea-user-{uuid.uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "Tarea User",
        "is_active": True,
    })
    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=tenant_id)
    return await usuario_repo.create({"user_id": user.id, "nombre": "Tarea", "apellidos": "User"})


async def _seed_tarea(db_session: AsyncSession, tenant_id: uuid.UUID, coord_usuario_id: uuid.UUID, **overrides) -> Tarea:
    from app.repositories.tarea_repository import TareaRepository
    repo = TareaRepository(session=db_session, tenant_id=tenant_id)
    data = {
        "asignado_a": coord_usuario_id,
        "asignado_por": coord_usuario_id,
        "descripcion": "Tarea test",
        "estado": TareaEstado.PENDIENTE.value,
    }
    data.update(overrides)
    return await repo.create(data)


# ── Create ──────────────────────────────────────────────────────────

class TestCreate:
    async def test_create_returns_201(self, client: AsyncClient, db_session, test_tenant, auth_user, coord_usuario):
        response = await client.post(
            "/api/v1/tareas",
            json={
                "asignado_a": str(coord_usuario.id),
                "descripcion": "Nueva tarea de prueba",
            },
        )
        assert response.status_code == 201
        body = response.json()
        assert body["descripcion"] == "Nueva tarea de prueba"
        assert body["estado"] == "PENDIENTE"

    async def test_create_returns_422_on_invalid(self, client: AsyncClient):
        response = await client.post("/api/v1/tareas", json={})
        assert response.status_code == 422

    async def test_create_without_perm_returns_403(self, client: AsyncClient, app, db_session, test_tenant):
        user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
        user = await user_repo.create({
            "email": f"nexo-{uuid.uuid4().hex[:8]}@test.com",
            "password_hash": "hash",
            "display_name": "Nexo",
            "is_active": True,
        })
        usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
        await usuario_repo.create({"user_id": user.id, "nombre": "Nexo", "apellidos": "Test"})
        no_perm = CurrentUser(user_id=user.id, tenant_id=test_tenant.id, roles=["NEXO"])
        async def _override():
            return no_perm
        app.dependency_overrides[get_current_user] = _override
        cleanup_permission_cache()

        response = await client.post(
            "/api/v1/tareas",
            json={"asignado_a": str(uuid.uuid4()), "descripcion": "Test"},
        )
        assert response.status_code == 403

    async def test_create_with_prof_returns_403(self, client: AsyncClient, app, db_session, test_tenant, auth_prof_user):
        async def _override():
            return auth_prof_user
        app.dependency_overrides[get_current_user] = _override
        cleanup_permission_cache()

        response = await client.post(
            "/api/v1/tareas",
            json={"asignado_a": str(uuid.uuid4()), "descripcion": "Test"},
        )
        assert response.status_code == 403


# ── State transition ────────────────────────────────────────────────

class TestCambiarEstado:
    async def test_transition_returns_200(self, client: AsyncClient, db_session, test_tenant, coord_usuario):
        t = await _seed_tarea(db_session, test_tenant.id, coord_usuario_id=coord_usuario.id, estado=TareaEstado.PENDIENTE.value)
        response = await client.patch(
            f"/api/v1/tareas/{t.id}/estado",
            json={"estado": "EN_PROGRESO"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["estado"] == "EN_PROGRESO"

    async def test_transition_with_comment(self, client: AsyncClient, db_session, test_tenant, coord_usuario):
        t = await _seed_tarea(db_session, test_tenant.id, coord_usuario_id=coord_usuario.id, estado=TareaEstado.PENDIENTE.value)
        response = await client.patch(
            f"/api/v1/tareas/{t.id}/estado",
            json={"estado": "EN_PROGRESO", "comentario": "Arranco ahora"},
        )
        assert response.status_code == 200
        body = response.json()
        assert len(body["comentarios"]) == 1
        assert body["comentarios"][0]["texto"] == "Arranco ahora"

    async def test_transition_invalid_returns_422(self, client: AsyncClient, db_session, test_tenant, coord_usuario):
        t = await _seed_tarea(db_session, test_tenant.id, coord_usuario_id=coord_usuario.id, estado=TareaEstado.PENDIENTE.value)
        response = await client.patch(
            f"/api/v1/tareas/{t.id}/estado",
            json={"estado": "RESUELTA"},
        )
        assert response.status_code == 422

    async def test_transition_not_found_returns_404(self, client: AsyncClient):
        response = await client.patch(
            f"/api/v1/tareas/{uuid.uuid4()}/estado",
            json={"estado": "EN_PROGRESO"},
        )
        assert response.status_code == 404


# ── Get single ──────────────────────────────────────────────────────

class TestGet:
    async def test_get_returns_200(self, client: AsyncClient, db_session, test_tenant, coord_usuario):
        t = await _seed_tarea(db_session, test_tenant.id, coord_usuario_id=coord_usuario.id)
        response = await client.get(f"/api/v1/tareas/{t.id}")
        assert response.status_code == 200
        body = response.json()
        assert body["id"] == str(t.id)
        assert "comentarios" in body

    async def test_get_not_found_returns_404(self, client: AsyncClient):
        response = await client.get(f"/api/v1/tareas/{uuid.uuid4()}")
        assert response.status_code == 404


# ── Delete ──────────────────────────────────────────────────────────

class TestDelete:
    async def test_delete_returns_204(self, client: AsyncClient, db_session, test_tenant, coord_usuario):
        t = await _seed_tarea(db_session, test_tenant.id, coord_usuario_id=coord_usuario.id)
        response = await client.delete(f"/api/v1/tareas/{t.id}")
        assert response.status_code == 204

    async def test_delete_not_found_returns_404(self, client: AsyncClient):
        response = await client.delete(f"/api/v1/tareas/{uuid.uuid4()}")
        assert response.status_code == 404

    async def test_delete_by_prof_returns_403(
        self, client: AsyncClient, app, db_session, test_tenant, auth_prof_user, coord_usuario,
    ):
        async def _override():
            return auth_prof_user
        app.dependency_overrides[get_current_user] = _override
        cleanup_permission_cache()

        t = await _seed_tarea(db_session, test_tenant.id, coord_usuario_id=coord_usuario.id)
        response = await client.delete(f"/api/v1/tareas/{t.id}")
        assert response.status_code == 403


# ── Mis tareas ──────────────────────────────────────────────────────

class TestMisTareas:
    async def test_mis_tareas_returns_200(self, client: AsyncClient, db_session, test_tenant, auth_user, coord_usuario):
        otro = await _make_usuario(db_session, test_tenant.id)
        await _seed_tarea(db_session, test_tenant.id, coord_usuario_id=coord_usuario.id, asignado_a=coord_usuario.id, descripcion="Mi tarea")
        await _seed_tarea(db_session, test_tenant.id, coord_usuario_id=coord_usuario.id, asignado_a=otro.id, descripcion="No es mia")

        response = await client.get("/api/v1/tareas/mias")
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 1
        assert body[0]["descripcion"] == "Mi tarea"

    async def test_mis_tareas_with_estado_filter(self, client: AsyncClient, db_session, test_tenant, auth_user, coord_usuario):
        await _seed_tarea(db_session, test_tenant.id, coord_usuario_id=coord_usuario.id, asignado_a=coord_usuario.id, estado=TareaEstado.PENDIENTE.value, descripcion="Pendiente")
        await _seed_tarea(db_session, test_tenant.id, coord_usuario_id=coord_usuario.id, asignado_a=coord_usuario.id, estado=TareaEstado.EN_PROGRESO.value, descripcion="En progreso")

        response = await client.get("/api/v1/tareas/mias?estado=EN_PROGRESO")
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 1
        assert body[0]["descripcion"] == "En progreso"


# ── Admin list ──────────────────────────────────────────────────────

class TestAdminList:
    async def test_list_returns_200(self, client: AsyncClient, db_session, test_tenant, coord_usuario):
        await _seed_tarea(db_session, test_tenant.id, coord_usuario_id=coord_usuario.id, descripcion="T1")
        await _seed_tarea(db_session, test_tenant.id, coord_usuario_id=coord_usuario.id, descripcion="T2")
        response = await client.get("/api/v1/tareas")
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 2


# ── Add comment ─────────────────────────────────────────────────────

class TestAddComentario:
    async def test_add_comentario_returns_201(self, client: AsyncClient, db_session, test_tenant, auth_user, coord_usuario):
        t = await _seed_tarea(db_session, test_tenant.id, coord_usuario_id=coord_usuario.id, asignado_a=coord_usuario.id)
        response = await client.post(
            f"/api/v1/tareas/{t.id}/comentarios",
            json={"texto": "Un comentario nuevo"},
        )
        assert response.status_code == 201
        body = response.json()
        assert body["texto"] == "Un comentario nuevo"
        assert body["tarea_id"] == str(t.id)

    async def test_add_comentario_not_found_returns_404(self, client: AsyncClient):
        response = await client.post(
            f"/api/v1/tareas/{uuid.uuid4()}/comentarios",
            json={"texto": "Comentario"},
        )
        assert response.status_code == 404

    async def test_add_comentario_returns_422_on_empty(self, client: AsyncClient, db_session, test_tenant, coord_usuario):
        t = await _seed_tarea(db_session, test_tenant.id, coord_usuario_id=coord_usuario.id)
        response = await client.post(
            f"/api/v1/tareas/{t.id}/comentarios",
            json={"texto": ""},
        )
        assert response.status_code == 422


# ── Auth guard ──────────────────────────────────────────────────────

class TestAuth:
    async def test_returns_401_without_auth(self, client: AsyncClient, app):
        app.dependency_overrides.pop(get_current_user, None)
        response = await client.get("/api/v1/tareas")
        assert response.status_code == 401

    async def test_mias_returns_401_without_auth(self, client: AsyncClient, app):
        app.dependency_overrides.pop(get_current_user, None)
        response = await client.get("/api/v1/tareas/mias")
        assert response.status_code == 401
