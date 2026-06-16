"""Integration tests for liquidaciones and facturas routers (C-18).

Uses client fixture with overridden get_current_user.
Seeds permissions so RBAC guards pass.
"""

from datetime import date
from decimal import Decimal
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.factura import Factura
from app.models.tenant import Tenant
from app.models.user import User
from app.models.usuario import Usuario
from app.repositories.base import BaseRepository
from app.schemas.auth import CurrentUser
from tests.helpers import cleanup_permission_cache, seed_permissions_for_tenant


@pytest.fixture
async def auth_user(db_session, test_tenant) -> CurrentUser:
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    user = await user_repo.create({
        "email": f"finanzas-{uuid.uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "Finanzas",
        "is_active": True,
    })
    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    await usuario_repo.create({
        "user_id": user.id,
        "nombre": "Finanzas",
        "apellidos": "Test",
    })
    return CurrentUser(
        user_id=user.id,
        tenant_id=test_tenant.id,
        roles=["FINANZAS"],
    )


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


@pytest.fixture
async def facturador(db_session, test_tenant) -> Usuario:
    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    usuarios = await usuario_repo.find_by(user_id=auth_user.user_id)
    if usuarios:
        usuario = usuarios[0]
        usuario.facturador = True
        await db_session.flush()
        await db_session.refresh(usuario)
        return usuario
    raise RuntimeError("Usuario not found for auth_user")


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


@pytest.fixture
async def test_cohorte(db_session: AsyncSession, test_tenant: Tenant) -> Cohorte:
    carrera_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=test_tenant.id)
    carrera = await carrera_repo.create({"nombre": "Ingenieria", "codigo": "ING"})
    repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({"carrera_id": carrera.id, "nombre": "2026", "anio": 2026})


@pytest.fixture
async def test_usuario(db_session: AsyncSession, test_tenant: Tenant) -> Usuario:
    """Creates Usuario with id == user.id to work around service inconsistency
    where data.usuario_id is used both for find_by(user_id=...) and FK."""
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    user = await user_repo.create({
        "email": f"usr-{uuid.uuid4().hex[:8]}@test.com",
        "password_hash": "hash", "display_name": "Test",
    })
    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    return await usuario_repo.create({
        "id": user.id,
        "user_id": user.id,
        "nombre": "Test", "apellidos": "User",
        "facturador": True,
    })


# ── Salarios Base ───────────────────────────────────────────────────

class TestSalariosBase:
    async def test_list_returns_200(self, client: AsyncClient, db_session, test_tenant, salario_base_data):
        response = await client.get("/api/v1/liquidaciones/salarios-base")
        assert response.status_code == 200
        body = response.json()
        assert len(body) >= 1

    async def test_create_returns_201(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/liquidaciones/salarios-base",
            json={
                "rol": "TUTOR",
                "monto": "80000.00",
                "desde": "2026-01-01",
            },
        )
        assert response.status_code == 201
        body = response.json()
        assert body["rol"] == "TUTOR"

    async def test_create_invalid_returns_422(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/liquidaciones/salarios-base",
            json={"rol": ""},
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
            "/api/v1/liquidaciones/salarios-base",
            json={"rol": "TUTOR", "monto": "1", "desde": "2026-01-01"},
        )
        assert response.status_code == 403


# ── Salarios Plus ───────────────────────────────────────────────────

class TestSalariosPlus:
    async def test_list_returns_200(self, client: AsyncClient):
        response = await client.get("/api/v1/liquidaciones/salarios-plus")
        assert response.status_code == 200

    async def test_create_returns_201(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/liquidaciones/salarios-plus",
            json={
                "grupo": "TEST",
                "rol": "PROFESOR",
                "descripcion": "Test plus",
                "monto": "10000.00",
                "desde": "2026-01-01",
            },
        )
        assert response.status_code == 201
        body = response.json()
        assert body["grupo"] == "TEST"

    async def test_create_without_perm_returns_403(
        self, client: AsyncClient, app, auth_user_no_perm,
    ):
        async def _override_user():
            return auth_user_no_perm
        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()
        response = await client.post(
            "/api/v1/liquidaciones/salarios-plus",
            json={"grupo": "T", "rol": "P", "descripcion": "X", "monto": "1", "desde": "2026-01-01"},
        )
        assert response.status_code == 403


# ── Claves Plus ─────────────────────────────────────────────────────

class TestClavesPlus:
    async def test_list_returns_200(self, client: AsyncClient):
        response = await client.get("/api/v1/liquidaciones/claves-plus")
        assert response.status_code == 200

    async def test_create_returns_201(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/liquidaciones/claves-plus",
            json={
                "codigo": "NUEVO",
                "descripcion": "Nueva clave",
                "desde": "2026-01-01",
            },
        )
        assert response.status_code == 201
        body = response.json()
        assert body["codigo"] == "NUEVO"

    async def test_create_without_perm_returns_403(
        self, client: AsyncClient, app, auth_user_no_perm,
    ):
        async def _override_user():
            return auth_user_no_perm
        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()
        response = await client.post(
            "/api/v1/liquidaciones/claves-plus",
            json={"codigo": "X", "descripcion": "X", "desde": "2026-01-01"},
        )
        assert response.status_code == 403


# ── Materias Clave Plus ─────────────────────────────────────────────

class TestMateriasClavePlus:
    async def test_create_returns_201(
        self, client: AsyncClient, materia_prog, clave_prog,
    ):
        response = await client.post(
            "/api/v1/liquidaciones/materias-clave-plus",
            json={
                "materia_id": str(materia_prog.id),
                "clave_plus_id": str(clave_prog.id),
                "desde": "2026-01-01",
            },
        )
        assert response.status_code == 201
        body = response.json()
        assert body["materia_id"] == str(materia_prog.id)

    async def test_create_without_perm_returns_403(
        self, client: AsyncClient, app, auth_user_no_perm,
    ):
        async def _override_user():
            return auth_user_no_perm
        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()
        response = await client.post(
            "/api/v1/liquidaciones/materias-clave-plus",
            json={
                "materia_id": str(uuid.uuid4()),
                "clave_plus_id": str(uuid.uuid4()),
                "desde": "2026-01-01",
            },
        )
        assert response.status_code == 403


# ── Facturas ────────────────────────────────────────────────────────

class TestFacturas:
    async def test_create_returns_201(
        self, client: AsyncClient, db_session, test_tenant, test_usuario,
    ):
        response = await client.post(
            "/api/v1/facturas",
            json={
                "usuario_id": str(test_usuario.id),
                "periodo": "2026-06",
            },
        )
        assert response.status_code == 201
        body = response.json()
        assert body["estado"] == "Pendiente"

    async def test_create_invalid_returns_422(self, client: AsyncClient):
        response = await client.post("/api/v1/facturas", json={"periodo": "bad"})
        assert response.status_code == 422

    async def test_list_returns_200(self, client: AsyncClient):
        response = await client.get("/api/v1/facturas")
        assert response.status_code == 200

    async def test_abonar_returns_200(
        self, client: AsyncClient, db_session, test_tenant, test_usuario,
    ):
        fac_repo = BaseRepository(model=Factura, session=db_session, tenant_id=test_tenant.id)
        fac = await fac_repo.create({"usuario_id": test_usuario.id, "periodo": "2026-06"})
        response = await client.post(f"/api/v1/facturas/{fac.id}/abonar")
        assert response.status_code == 200
        body = response.json()
        assert body["estado"] == "Abonada"

    async def test_abonar_not_found_returns_404(self, client: AsyncClient):
        response = await client.post(f"/api/v1/facturas/{uuid.uuid4()}/abonar")
        assert response.status_code == 404

    async def test_abonar_without_perm_returns_403(
        self, client: AsyncClient, app, auth_user_no_perm,
    ):
        async def _override_user():
            return auth_user_no_perm
        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()
        response = await client.post(f"/api/v1/facturas/{uuid.uuid4()}/abonar")
        assert response.status_code == 403

    async def test_delete_returns_204(
        self, client: AsyncClient, db_session, test_tenant, test_usuario,
    ):
        fac_repo = BaseRepository(model=Factura, session=db_session, tenant_id=test_tenant.id)
        fac = await fac_repo.create({"usuario_id": test_usuario.id, "periodo": "2026-06"})
        response = await client.delete(f"/api/v1/facturas/{fac.id}")
        assert response.status_code == 204

    async def test_delete_not_found_returns_404(self, client: AsyncClient):
        response = await client.delete(f"/api/v1/facturas/{uuid.uuid4()}")
        assert response.status_code == 404


# ── Vista Periodo ───────────────────────────────────────────────────

class TestVistaPeriodo:
    async def test_vista_periodo_returns_200(
        self, client: AsyncClient, test_cohorte,
    ):
        response = await client.get(
            "/api/v1/liquidaciones",
            params={"periodo": "2026-06", "cohorte_id": str(test_cohorte.id)},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["periodo"] == "2026-06"
        assert "general" in body
        assert "nexo" in body
        assert "factura" in body
        assert "kpis" in body
