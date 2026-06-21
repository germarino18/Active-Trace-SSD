"""Integration tests for owner-only tarea endpoints (group 7a).

Routes under test:
  POST  /api/v1/tareas/mias   — profesor creates own task
  PATCH /api/v1/tareas/mias/{id} — profesor edits own task (owner-only)
"""

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


# ── Fixtures ────────────────────────────────────────────────────────


@pytest.fixture
async def prof_user(db_session, test_tenant) -> User:
    repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({
        "email": f"prof-mias-{uuid.uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "Profesor Mias",
        "is_active": True,
    })


@pytest.fixture
async def prof_usuario(db_session, test_tenant, prof_user) -> Usuario:
    repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({"user_id": prof_user.id, "nombre": "Prof", "apellidos": "Mias"})


@pytest.fixture
async def auth_prof(prof_user, test_tenant) -> CurrentUser:
    return CurrentUser(user_id=prof_user.id, tenant_id=test_tenant.id, roles=["PROFESOR"])


@pytest.fixture
async def other_prof_user(db_session, test_tenant) -> User:
    repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({
        "email": f"prof2-mias-{uuid.uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "Profesor Otro",
        "is_active": True,
    })


@pytest.fixture
async def other_prof_usuario(db_session, test_tenant, other_prof_user) -> Usuario:
    repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({"user_id": other_prof_user.id, "nombre": "Otro", "apellidos": "Prof"})


@pytest.fixture
async def auth_other_prof(other_prof_user, test_tenant) -> CurrentUser:
    return CurrentUser(user_id=other_prof_user.id, tenant_id=test_tenant.id, roles=["PROFESOR"])


@pytest.fixture(autouse=True)
async def _setup_auth(app, db_session, test_tenant, auth_prof, prof_usuario):
    async def _override():
        return auth_prof

    app.dependency_overrides[get_current_user] = _override
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    cleanup_permission_cache()
    yield
    app.dependency_overrides.pop(get_current_user, None)
    cleanup_permission_cache()


async def _seed_tarea_for(
    db_session: AsyncSession,
    tenant_id: uuid.UUID,
    asignado_a: uuid.UUID,
    asignado_por: uuid.UUID,
    **overrides,
) -> Tarea:
    from app.repositories.tarea_repository import TareaRepository
    repo = TareaRepository(session=db_session, tenant_id=tenant_id)
    data = {
        "asignado_a": asignado_a,
        "asignado_por": asignado_por,
        "descripcion": "Tarea test",
        "estado": TareaEstado.PENDIENTE.value,
    }
    data.update(overrides)
    return await repo.create(data)


# ── 7a.2 POST /api/v1/tareas/mias ───────────────────────────────────


class TestCreatePropia:
    async def test_create_own_tarea_returns_201(
        self, client: AsyncClient, db_session, test_tenant, prof_usuario
    ):
        """PROF creates a task assigned to themselves — happy path."""
        response = await client.post(
            "/api/v1/tareas/mias",
            json={"descripcion": "Mi propia tarea"},
        )
        assert response.status_code == 201
        body = response.json()
        assert body["descripcion"] == "Mi propia tarea"
        assert body["estado"] == "PENDIENTE"
        # owner must be the authenticated user, never from body
        assert body["asignado_a"] == str(prof_usuario.id)
        assert body["asignado_por"] == str(prof_usuario.id)

    async def test_create_with_materia_id_null_returns_201(
        self, client: AsyncClient, db_session, test_tenant, prof_usuario
    ):
        """PROF creates task with materia_id explicitly null (optional field)."""
        response = await client.post(
            "/api/v1/tareas/mias",
            json={"descripcion": "Tarea sin materia", "materia_id": None},
        )
        assert response.status_code == 201
        body = response.json()
        assert body["materia_id"] is None
        assert body["asignado_a"] == str(prof_usuario.id)

    async def test_create_unknown_field_returns_422(self, client: AsyncClient):
        """extra='forbid' — unknown body fields must return 422."""
        response = await client.post(
            "/api/v1/tareas/mias",
            json={"descripcion": "Test", "asignado_a": str(uuid.uuid4())},
        )
        assert response.status_code == 422

    async def test_create_empty_descripcion_returns_422(self, client: AsyncClient):
        """Descripcion must have min_length=1."""
        response = await client.post(
            "/api/v1/tareas/mias",
            json={"descripcion": ""},
        )
        assert response.status_code == 422

    async def test_create_missing_descripcion_returns_422(self, client: AsyncClient):
        """Descripcion is required."""
        response = await client.post("/api/v1/tareas/mias", json={})
        assert response.status_code == 422

    async def test_create_without_auth_returns_401(self, client: AsyncClient, app):
        """No auth token → 401."""
        app.dependency_overrides.pop(get_current_user, None)
        response = await client.post(
            "/api/v1/tareas/mias",
            json={"descripcion": "Sin auth"},
        )
        assert response.status_code == 401


# ── 7a.3 PATCH /api/v1/tareas/mias/{id} ─────────────────────────────


class TestUpdatePropia:
    async def test_update_descripcion_returns_200(
        self, client: AsyncClient, db_session, test_tenant, prof_usuario
    ):
        """Owner updates descripcion — happy path."""
        t = await _seed_tarea_for(
            db_session, test_tenant.id,
            asignado_a=prof_usuario.id,
            asignado_por=prof_usuario.id,
            descripcion="Original",
        )
        response = await client.patch(
            f"/api/v1/tareas/mias/{t.id}",
            json={"descripcion": "Actualizada"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["descripcion"] == "Actualizada"
        assert body["id"] == str(t.id)

    async def test_update_all_fields_returns_200(
        self, client: AsyncClient, db_session, test_tenant, prof_usuario
    ):
        """Owner updates both descripcion and estado — triangulate multiple fields."""
        t = await _seed_tarea_for(
            db_session, test_tenant.id,
            asignado_a=prof_usuario.id,
            asignado_por=prof_usuario.id,
            descripcion="Primera desc",
            estado=TareaEstado.PENDIENTE.value,
        )
        response = await client.patch(
            f"/api/v1/tareas/mias/{t.id}",
            json={"descripcion": "Segunda desc", "estado": "EN_PROGRESO"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["descripcion"] == "Segunda desc"
        assert body["estado"] == "EN_PROGRESO"

    async def test_update_estado_returns_200(
        self, client: AsyncClient, db_session, test_tenant, prof_usuario
    ):
        """Owner can change estado via PATCH /mias/{id} (uses state machine)."""
        t = await _seed_tarea_for(
            db_session, test_tenant.id,
            asignado_a=prof_usuario.id,
            asignado_por=prof_usuario.id,
            estado=TareaEstado.PENDIENTE.value,
        )
        response = await client.patch(
            f"/api/v1/tareas/mias/{t.id}",
            json={"estado": "EN_PROGRESO"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["estado"] == "EN_PROGRESO"

    async def test_update_not_owner_returns_404(
        self,
        client: AsyncClient,
        app,
        db_session,
        test_tenant,
        prof_usuario,
        other_prof_usuario,
        auth_other_prof,
    ):
        """Another profesor cannot edit the task — 404 (no existence leak)."""
        t = await _seed_tarea_for(
            db_session, test_tenant.id,
            asignado_a=prof_usuario.id,
            asignado_por=prof_usuario.id,
            descripcion="No tuya",
        )
        # Switch to other profesor
        async def _override():
            return auth_other_prof

        app.dependency_overrides[get_current_user] = _override
        cleanup_permission_cache()

        response = await client.patch(
            f"/api/v1/tareas/mias/{t.id}",
            json={"descripcion": "Intento de edición ajena"},
        )
        assert response.status_code == 404

    async def test_update_nonexistent_returns_404(
        self, client: AsyncClient
    ):
        """Non-existent tarea_id → 404."""
        response = await client.patch(
            f"/api/v1/tareas/mias/{uuid.uuid4()}",
            json={"descripcion": "Fantasma"},
        )
        assert response.status_code == 404

    async def test_update_unknown_field_returns_422(
        self, client: AsyncClient, db_session, test_tenant, prof_usuario
    ):
        """extra='forbid' — unknown body fields → 422."""
        t = await _seed_tarea_for(
            db_session, test_tenant.id,
            asignado_a=prof_usuario.id,
            asignado_por=prof_usuario.id,
        )
        response = await client.patch(
            f"/api/v1/tareas/mias/{t.id}",
            json={"descripcion": "Test", "campo_extra": "malo"},
        )
        assert response.status_code == 422

    async def test_update_without_auth_returns_401(
        self, client: AsyncClient, app, db_session, test_tenant, prof_usuario
    ):
        """No auth token → 401."""
        t = await _seed_tarea_for(
            db_session, test_tenant.id,
            asignado_a=prof_usuario.id,
            asignado_por=prof_usuario.id,
        )
        app.dependency_overrides.pop(get_current_user, None)
        response = await client.patch(
            f"/api/v1/tareas/mias/{t.id}",
            json={"descripcion": "Sin auth"},
        )
        assert response.status_code == 401

    async def test_update_tenant_isolation(
        self,
        client: AsyncClient,
        db_session,
        test_tenant,
        another_tenant,
        prof_usuario,
        auth_prof,
    ):
        """A tarea from another tenant is invisible (404)."""
        # Create task in another_tenant (same usuario ID, different tenant)
        from app.repositories.tarea_repository import TareaRepository
        other_repo = TareaRepository(session=db_session, tenant_id=another_tenant.id)
        t_other = await other_repo.create({
            "asignado_a": prof_usuario.id,
            "asignado_por": prof_usuario.id,
            "descripcion": "Otro tenant",
            "estado": TareaEstado.PENDIENTE.value,
        })
        # Client is scoped to test_tenant → must 404
        response = await client.patch(
            f"/api/v1/tareas/mias/{t_other.id}",
            json={"descripcion": "Intento cross-tenant"},
        )
        assert response.status_code == 404
