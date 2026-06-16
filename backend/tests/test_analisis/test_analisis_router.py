import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.repositories.base import BaseRepository
from app.repositories.calificacion_repository import CalificacionRepository
from app.repositories.dictado_repository import DictadoRepository
from app.repositories.entrada_padron_repository import EntradaPadronRepository
from app.repositories.version_padron_repository import VersionPadronRepository
from app.schemas.auth import CurrentUser
from tests.helpers import cleanup_permission_cache, seed_permissions_for_tenant


@pytest.fixture
async def auth_user(db_session, test_tenant) -> CurrentUser:
    """Create a real User + return CurrentUser with ADMIN role."""
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
    """User with ALUMNO role (no ANALISIS permissions)."""
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


async def _create_dictado(db_session: AsyncSession, tenant_id: uuid.UUID) -> dict:
    from app.models.carrera import Carrera
    from app.models.cohorte import Cohorte
    from app.models.materia import Materia
    from app.models.entrada_padron import EntradaPadron
    from app.models.version_padron import VersionPadron

    c_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=tenant_id)
    carrera = await c_repo.create({"codigo": "ING-INF", "nombre": "Ingeniería"})
    m_repo = BaseRepository(model=Materia, session=db_session, tenant_id=tenant_id)
    materia = await m_repo.create({"codigo": "MAT-101", "nombre": "Matemáticas"})
    co_repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=tenant_id)
    cohorte = await co_repo.create({"carrera_id": carrera.id, "nombre": "2024", "anio": 2024})
    d_repo = DictadoRepository(session=db_session, tenant_id=tenant_id)
    dictado = await d_repo.create(
        {"materia_id": materia.id, "carrera_id": carrera.id, "cohorte_id": cohorte.id}
    )
    return {"dictado": dictado}


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


class TestAtrasados:
    async def test_get_atrasados_returns_200(
        self, client: AsyncClient, db_session, test_tenant, auth_user
    ):
        data = await _create_dictado(db_session, test_tenant.id)
        response = await client.get(
            "/api/admin/analisis/atrasados",
            params={"dictado_id": str(data["dictado"].id)},
        )
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_atrasados_without_perm_returns_403(
        self, client: AsyncClient, app, auth_user_no_perm
    ):
        async def _override_user():
            return auth_user_no_perm

        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()

        response = await client.get(
            "/api/admin/analisis/atrasados",
            params={"dictado_id": str(uuid.uuid4())},
        )
        assert response.status_code == 403


class TestRanking:
    async def test_get_ranking_returns_200(
        self, client: AsyncClient, db_session, test_tenant, auth_user
    ):
        data = await _create_dictado(db_session, test_tenant.id)
        response = await client.get(
            "/api/admin/analisis/ranking",
            params={"dictado_id": str(data["dictado"].id)},
        )
        assert response.status_code == 200

    async def test_get_ranking_without_perm_returns_403(
        self, client: AsyncClient, app, auth_user_no_perm
    ):
        async def _override_user():
            return auth_user_no_perm

        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()

        response = await client.get(
            "/api/admin/analisis/ranking",
            params={"dictado_id": str(uuid.uuid4())},
        )
        assert response.status_code == 403


class TestReporteMateria:
    async def test_get_reporte_returns_200(
        self, client: AsyncClient, db_session, test_tenant, auth_user
    ):
        data = await _create_dictado(db_session, test_tenant.id)
        response = await client.get(
            f"/api/admin/analisis/reportes/materia/{data['dictado'].id}",
        )
        assert response.status_code == 200
        body = response.json()
        assert body["sin_datos"] is True

    async def test_get_reporte_without_perm_returns_403(
        self, client: AsyncClient, app, auth_user_no_perm
    ):
        async def _override_user():
            return auth_user_no_perm

        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()

        response = await client.get(
            f"/api/admin/analisis/reportes/materia/{uuid.uuid4()}",
        )
        assert response.status_code == 403


class TestNotasFinales:
    async def test_get_notas_returns_200(
        self, client: AsyncClient, db_session, test_tenant, auth_user
    ):
        data = await _create_dictado(db_session, test_tenant.id)
        response = await client.get(
            "/api/admin/analisis/notas-finales",
            params={"dictado_id": str(data["dictado"].id)},
        )
        assert response.status_code == 200

    async def test_get_notas_without_perm_returns_403(
        self, client: AsyncClient, app, auth_user_no_perm
    ):
        async def _override_user():
            return auth_user_no_perm

        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()

        response = await client.get(
            "/api/admin/analisis/notas-finales",
            params={"dictado_id": str(uuid.uuid4())},
        )
        assert response.status_code == 403


class TestTPSinCorregir:
    async def test_get_tps_sin_finalizaciones_returns_400(
        self, client: AsyncClient, db_session, test_tenant, auth_user
    ):
        data = await _create_dictado(db_session, test_tenant.id)
        response = await client.get(
            "/api/admin/analisis/tps-sin-corregir/export",
            params={"dictado_id": str(data["dictado"].id)},
        )
        assert response.status_code == 400

    async def test_get_tps_without_perm_returns_403(
        self, client: AsyncClient, app, auth_user_no_perm
    ):
        async def _override_user():
            return auth_user_no_perm

        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()

        response = await client.get(
            "/api/admin/analisis/tps-sin-corregir/export",
            params={"dictado_id": str(uuid.uuid4())},
        )
        assert response.status_code == 403


class TestMonitorGeneral:
    async def test_get_monitor_general_returns_200(
        self, client: AsyncClient, db_session, test_tenant, auth_user
    ):
        response = await client.get("/api/admin/analisis/monitor/general")
        assert response.status_code == 200
        body = response.json()
        assert "items" in body
        assert "total_count" in body

    async def test_get_monitor_general_without_perm_returns_403(
        self, client: AsyncClient, app, auth_user_no_perm
    ):
        async def _override_user():
            return auth_user_no_perm

        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()

        response = await client.get("/api/admin/analisis/monitor/general")
        assert response.status_code == 403


class TestMonitorSeguimiento:
    async def test_get_monitor_seguimiento_returns_200(
        self, client: AsyncClient, db_session, test_tenant, auth_user
    ):
        response = await client.get("/api/admin/analisis/monitor/seguimiento")
        assert response.status_code == 200

    async def test_get_monitor_seguimiento_without_perm_returns_403(
        self, client: AsyncClient, app, auth_user_no_perm
    ):
        async def _override_user():
            return auth_user_no_perm

        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()

        response = await client.get("/api/admin/analisis/monitor/seguimiento")
        assert response.status_code == 403
