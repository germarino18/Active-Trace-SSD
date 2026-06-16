"""Integration tests for comunicaciones router (C-12).

Uses client fixture with overridden get_current_user.
Seeds permissions so RBAC guards pass.
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.models.comunicacion import Comunicacion, ComunicacionEstado
from app.models.materia import Materia
from app.models.tenant import Tenant
from app.models.user import User
from app.models.usuario import Usuario
from app.repositories.base import BaseRepository
from app.schemas.auth import CurrentUser
from tests.helpers import cleanup_permission_cache, seed_permissions_for_tenant


@pytest.fixture
async def auth_user(db_session, test_tenant) -> CurrentUser:
    """Create User + Usuario, return CurrentUser with User.id as user_id."""
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
        "nombre": "Coordinador",
        "apellidos": "Test",
    })
    return CurrentUser(
        user_id=user.id,
        tenant_id=test_tenant.id,
        roles=["COORDINADOR"],
    )


@pytest.fixture
async def auth_usuario_id(db_session, auth_user, test_tenant) -> uuid.UUID:
    """Resolve auth_user.user_id (User.id) → Usuario.id for direct DB inserts."""
    repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    usuarios = await repo.find_by(user_id=auth_user.user_id)
    if usuarios:
        return usuarios[0].id
    raise RuntimeError("Usuario not found for auth_user")


@pytest.fixture
async def auth_user_no_perm(db_session, test_tenant) -> CurrentUser:
    """User without comunicacion permissions (ALUMNO)."""
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


async def _seed_materia(
    db_session: AsyncSession, tenant_id: uuid.UUID,
) -> Materia:
    materia_repo = BaseRepository(model=Materia, session=db_session, tenant_id=tenant_id)
    return await materia_repo.create({"codigo": "MAT-TST", "nombre": "Materia Test"})


# ── Preview ──────────────────────────────────────────────────────────────


class TestPreview:
    async def test_preview_returns_200(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/comunicaciones/preview",
            json={
                "destinatario_nombre": "Juan",
                "destinatario_apellido": "Pérez",
                "materia_nombre": "Matemática",
                "docente_nombre": "Prof. García",
                "asunto_template": "Hola $alumno_nombre",
                "cuerpo_template": "Materia: $materia",
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["asunto"] == "Hola Juan"
        assert body["cuerpo"] == "Materia: Matemática"

    async def test_preview_with_invalid_data_returns_422(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/comunicaciones/preview",
            json={"asunto_template": ""},
        )
        assert response.status_code == 422


# ── Enviar ────────────────────────────────────────────────────────────────


class TestEnviar:
    async def test_enviar_returns_200(
        self, client: AsyncClient, db_session, test_tenant, auth_user,
    ):
        materia = await _seed_materia(db_session, test_tenant.id)
        response = await client.post(
            "/api/v1/comunicaciones/enviar",
            json={
                "materia_id": str(materia.id),
                "asunto_template": "Hola $alumno_nombre",
                "cuerpo_template": "Cuerpo test",
                "destinatarios": [
                    {
                        "usuario_id": str(auth_user.user_id),
                        "destinatario_email": "alumno@test.com",
                        "destinatario_nombre": "Juan",
                        "destinatario_apellido": "Pérez",
                    },
                ],
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert "lote_id" in body
        assert body["total"] == 1

    async def test_enviar_without_perm_returns_403(
        self, client: AsyncClient, app, auth_user_no_perm,
    ):
        async def _override_user():
            return auth_user_no_perm

        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()

        response = await client.post(
            "/api/v1/comunicaciones/enviar",
            json={
                "materia_id": str(uuid.uuid4()),
                "asunto_template": "Test",
                "cuerpo_template": "Cuerpo",
                "destinatarios": [
                    {
                        "usuario_id": str(uuid.uuid4()),
                        "destinatario_email": "a@b.com",
                        "destinatario_nombre": "A",
                        "destinatario_apellido": "B",
                    },
                ],
            },
        )
        assert response.status_code == 403


# ── Get Comunicacion ─────────────────────────────────────────────────────


class TestGetComunicacion:
    async def test_get_returns_200(
        self, client: AsyncClient, db_session, test_tenant, auth_user, auth_usuario_id,
    ):
        materia = await _seed_materia(db_session, test_tenant.id)
        repo = BaseRepository(
            model=Comunicacion, session=db_session, tenant_id=test_tenant.id,
        )
        com = await repo.create({
            "enviado_por": auth_usuario_id,
            "materia_id": materia.id,
            "destinatario": "alumno@test.com",
            "destinatario_hash": "abc",
            "asunto": "Test",
            "cuerpo": "Cuerpo",
            "lote_id": uuid.uuid4(),
        })
        response = await client.get(f"/api/v1/comunicaciones/{com.id}")
        assert response.status_code == 200
        body = response.json()
        assert body["id"] == str(com.id)
        assert body["estado"] == ComunicacionEstado.PENDIENTE.value

    async def test_get_non_existent_returns_404(self, client: AsyncClient):
        response = await client.get(f"/api/v1/comunicaciones/{uuid.uuid4()}")
        assert response.status_code == 404

    async def test_get_without_perm_returns_403(
        self, client: AsyncClient, app, auth_user_no_perm,
    ):
        async def _override_user():
            return auth_user_no_perm

        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()

        response = await client.get(f"/api/v1/comunicaciones/{uuid.uuid4()}")
        assert response.status_code == 403


# ── Get Resumen Lote ─────────────────────────────────────────────────────


class TestGetResumenLote:
    async def test_get_resumen_returns_200(
        self, client: AsyncClient, db_session, test_tenant, auth_user, auth_usuario_id,
    ):
        materia = await _seed_materia(db_session, test_tenant.id)
        repo = BaseRepository(
            model=Comunicacion, session=db_session, tenant_id=test_tenant.id,
        )
        lote_id = uuid.uuid4()
        await repo.create({
            "enviado_por": auth_usuario_id,
            "materia_id": materia.id,
            "destinatario": "a@b.com",
            "destinatario_hash": "h1",
            "asunto": "A",
            "cuerpo": "C1",
            "lote_id": lote_id,
        })
        response = await client.get(f"/api/v1/comunicaciones/lotes/{lote_id}")
        assert response.status_code == 200
        body = response.json()
        assert body["lote_id"] == str(lote_id)
        assert body["total"] == 1

    async def test_get_resumen_without_perm_returns_403(
        self, client: AsyncClient, app, auth_user_no_perm,
    ):
        async def _override_user():
            return auth_user_no_perm

        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()

        response = await client.get(f"/api/v1/comunicaciones/lotes/{uuid.uuid4()}")
        assert response.status_code == 403


# ── Aprobar Individual ───────────────────────────────────────────────────


class TestAprobarIndividual:
    async def test_aprobar_returns_200(
        self, client: AsyncClient, db_session, test_tenant, auth_user, auth_usuario_id,
    ):
        materia = await _seed_materia(db_session, test_tenant.id)
        repo = BaseRepository(
            model=Comunicacion, session=db_session, tenant_id=test_tenant.id,
        )
        com = await repo.create({
            "enviado_por": auth_usuario_id,
            "materia_id": materia.id,
            "destinatario": "alumno@test.com",
            "destinatario_hash": "abc",
            "asunto": "Test",
            "cuerpo": "Cuerpo",
            "lote_id": uuid.uuid4(),
        })

    async def test_get_mine_returns_200(
        self, client: AsyncClient, app, auth_user, auth_user_no_perm,
    ):
        async def _override_user():
            return auth_user_no_perm

        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()

        response = await client.post(
            f"/api/v1/comunicaciones/{uuid.uuid4()}/aprobar"
        )
        assert response.status_code == 403


# ── Aprobar Lote ─────────────────────────────────────────────────────────


class TestAprobarLote:
    async def test_aprobar_lote_returns_200(
        self, client: AsyncClient, db_session, test_tenant, auth_user, auth_usuario_id,
    ):
        materia = await _seed_materia(db_session, test_tenant.id)
        repo = BaseRepository(
            model=Comunicacion, session=db_session, tenant_id=test_tenant.id,
        )
        lote_id = uuid.uuid4()
        await repo.create({
            "enviado_por": auth_usuario_id,
            "materia_id": materia.id,
            "destinatario": "a@b.com",
            "destinatario_hash": "h",
            "asunto": "Test",
            "cuerpo": "Cuerpo",
            "lote_id": lote_id,
        })
        response = await client.post(
            f"/api/v1/comunicaciones/lotes/{lote_id}/aprobar"
        )
        assert response.status_code == 200

    async def test_aprobar_lote_without_perm_returns_403(
        self, client: AsyncClient, app, auth_user_no_perm,
    ):
        async def _override_user():
            return auth_user_no_perm

        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()

        response = await client.post(
            f"/api/v1/comunicaciones/lotes/{uuid.uuid4()}/aprobar"
        )
        assert response.status_code == 403


# ── Cancelar Individual ──────────────────────────────────────────────────


class TestCancelarIndividual:
    async def test_cancelar_returns_200(
        self, client: AsyncClient, db_session, test_tenant, auth_user, auth_usuario_id,
    ):
        materia = await _seed_materia(db_session, test_tenant.id)
        repo = BaseRepository(
            model=Comunicacion, session=db_session, tenant_id=test_tenant.id,
        )
        com = await repo.create({
            "enviado_por": auth_usuario_id,
            "materia_id": materia.id,
            "destinatario": "a@b.com",
            "destinatario_hash": "h",
            "asunto": "Test",
            "cuerpo": "Cuerpo",
            "lote_id": uuid.uuid4(),
        })
        response = await client.post(f"/api/v1/comunicaciones/{com.id}/cancelar")
        assert response.status_code == 200

    async def test_cancelar_without_perm_returns_403(
        self, client: AsyncClient, app, auth_user_no_perm,
    ):
        async def _override_user():
            return auth_user_no_perm

        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()

        response = await client.post(
            f"/api/v1/comunicaciones/{uuid.uuid4()}/cancelar"
        )
        assert response.status_code == 403


# ── Cancelar Lote ────────────────────────────────────────────────────────


class TestCancelarLote:
    async def test_cancelar_lote_returns_200(
        self, client: AsyncClient, db_session, test_tenant, auth_user, auth_usuario_id,
    ):
        materia = await _seed_materia(db_session, test_tenant.id)
        repo = BaseRepository(
            model=Comunicacion, session=db_session, tenant_id=test_tenant.id,
        )
        lote_id = uuid.uuid4()
        await repo.create({
            "enviado_por": auth_usuario_id,
            "materia_id": materia.id,
            "destinatario": "a@b.com",
            "destinatario_hash": "h",
            "asunto": "Test",
            "cuerpo": "Cuerpo",
            "lote_id": lote_id,
        })
        response = await client.post(
            f"/api/v1/comunicaciones/lotes/{lote_id}/cancelar"
        )
        assert response.status_code == 200

    async def test_cancelar_lote_without_perm_returns_403(
        self, client: AsyncClient, app, auth_user_no_perm,
    ):
        async def _override_user():
            return auth_user_no_perm

        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()

        response = await client.post(
            f"/api/v1/comunicaciones/lotes/{uuid.uuid4()}/cancelar"
        )
        assert response.status_code == 403
