"""Integration tests for actividades router (C-25 §3.5).

TDD cycle: RED → GREEN → TRIANGULATE → REFACTOR.
Tests cover: crear, listar, editar, soft-delete, tenant isolation, RBAC 403.
"""

import datetime
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.materia import Materia
from app.models.user import User
from app.repositories.base import BaseRepository
from app.repositories.dictado_repository import DictadoRepository
from app.schemas.auth import CurrentUser
from tests.helpers import cleanup_permission_cache, seed_permissions_for_tenant


# ── Fixtures ──────────────────────────────────────────────────────────────────


async def _create_dictado(db_session: AsyncSession, tenant_id: uuid.UUID) -> uuid.UUID:
    """Create carrera, materia, cohorte, dictado for a tenant. Returns dictado.id."""
    c_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=tenant_id)
    carrera = await c_repo.create({"codigo": f"ING-{uuid.uuid4().hex[:4]}", "nombre": "Ingeniería"})
    m_repo = BaseRepository(model=Materia, session=db_session, tenant_id=tenant_id)
    materia = await m_repo.create({"codigo": f"MAT-{uuid.uuid4().hex[:4]}", "nombre": "Matemática"})
    co_repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=tenant_id)
    cohorte = await co_repo.create({"carrera_id": carrera.id, "nombre": "2024", "anio": 2024})
    d_repo = DictadoRepository(session=db_session, tenant_id=tenant_id)
    dictado = await d_repo.create(
        {"materia_id": materia.id, "carrera_id": carrera.id, "cohorte_id": cohorte.id}
    )
    return dictado.id


@pytest.fixture
async def auth_user(db_session, test_tenant) -> CurrentUser:
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    user = await user_repo.create(
        {
            "email": f"prof-{uuid.uuid4().hex[:8]}@test.com",
            "password_hash": "hash",
            "display_name": "Profesor",
            "is_active": True,
            "roles": ["PROFESOR"],
        }
    )
    return CurrentUser(user_id=user.id, tenant_id=test_tenant.id, roles=["PROFESOR"])


@pytest.fixture
async def auth_user_no_perm(db_session, test_tenant) -> CurrentUser:
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    user = await user_repo.create(
        {
            "email": f"alumno-{uuid.uuid4().hex[:8]}@test.com",
            "password_hash": "hash",
            "display_name": "Alumno",
            "is_active": True,
            "roles": ["ALUMNO"],
        }
    )
    return CurrentUser(user_id=user.id, tenant_id=test_tenant.id, roles=["ALUMNO"])


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


# ── §3 CRUD Actividad ─────────────────────────────────────────────────────────


class TestCrearActividad:
    """RED → GREEN → TRIANGULATE for crear actividad."""

    async def test_crear_actividad_returns_201(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
    ):
        """GREEN: crear actividad devuelve 201 con datos correctos."""
        dictado_id = await _create_dictado(db_session, test_tenant.id)

        resp = await client.post(
            f"/api/v1/actividades/dictados/{dictado_id}",
            json={"nombre": "TP1", "tipo": "TP", "fecha_limite": "2026-07-01"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["nombre"] == "TP1"
        assert data["tipo"] == "TP"
        assert data["fecha_limite"] == "2026-07-01"
        assert data["dictado_id"] == str(dictado_id)

    async def test_crear_actividad_sin_fecha_limite(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
    ):
        """TRIANGULATE: actividad sin fecha_limite también se crea."""
        dictado_id = await _create_dictado(db_session, test_tenant.id)

        resp = await client.post(
            f"/api/v1/actividades/dictados/{dictado_id}",
            json={"nombre": "Parcial 1", "tipo": "Parcial"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["nombre"] == "Parcial 1"
        assert data["fecha_limite"] is None

    async def test_crear_campo_extra_rechazado(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
    ):
        """Campo no declarado en schema → 422 (extra='forbid')."""
        dictado_id = await _create_dictado(db_session, test_tenant.id)

        resp = await client.post(
            f"/api/v1/actividades/dictados/{dictado_id}",
            json={"nombre": "TP2", "tipo": "TP", "campo_extra": "no"},
        )
        assert resp.status_code == 422


class TestListarActividades:
    """Listar actividades del dictado."""

    async def test_listar_solo_vivas(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
    ):
        """GREEN: listar devuelve actividades no soft-deleted."""
        dictado_id = await _create_dictado(db_session, test_tenant.id)

        # Create two actividades
        await client.post(
            f"/api/v1/actividades/dictados/{dictado_id}",
            json={"nombre": "TP1", "tipo": "TP"},
        )
        resp2 = await client.post(
            f"/api/v1/actividades/dictados/{dictado_id}",
            json={"nombre": "Parcial", "tipo": "Parcial"},
        )
        actividad2_id = resp2.json()["id"]

        # Soft-delete the second one
        await client.delete(f"/api/v1/actividades/{actividad2_id}")

        resp = await client.get(f"/api/v1/actividades/dictados/{dictado_id}")
        assert resp.status_code == 200
        nombres = [a["nombre"] for a in resp.json()]
        assert "TP1" in nombres
        assert "Parcial" not in nombres

    async def test_listar_dictado_sin_actividades(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
    ):
        """TRIANGULATE: dictado sin actividades devuelve lista vacía."""
        dictado_id = await _create_dictado(db_session, test_tenant.id)
        resp = await client.get(f"/api/v1/actividades/dictados/{dictado_id}")
        assert resp.status_code == 200
        assert resp.json() == []


class TestEditarActividad:
    """Editar fecha y otros campos."""

    async def test_editar_fecha_limite(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
    ):
        """GREEN: editar fecha_limite actualiza el campo."""
        dictado_id = await _create_dictado(db_session, test_tenant.id)
        create_resp = await client.post(
            f"/api/v1/actividades/dictados/{dictado_id}",
            json={"nombre": "TP3", "tipo": "TP", "fecha_limite": "2026-07-01"},
        )
        actividad_id = create_resp.json()["id"]

        resp = await client.patch(
            f"/api/v1/actividades/{actividad_id}",
            json={"fecha_limite": "2026-08-15"},
        )
        assert resp.status_code == 200
        assert resp.json()["fecha_limite"] == "2026-08-15"

    async def test_editar_nombre(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
    ):
        """TRIANGULATE: editar nombre."""
        dictado_id = await _create_dictado(db_session, test_tenant.id)
        create_resp = await client.post(
            f"/api/v1/actividades/dictados/{dictado_id}",
            json={"nombre": "TP3", "tipo": "TP"},
        )
        actividad_id = create_resp.json()["id"]

        resp = await client.patch(
            f"/api/v1/actividades/{actividad_id}",
            json={"nombre": "TP3 Actualizado"},
        )
        assert resp.status_code == 200
        assert resp.json()["nombre"] == "TP3 Actualizado"


class TestSoftDeleteActividad:
    """Soft delete verification."""

    async def test_soft_delete_no_hard_delete(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
    ):
        """GREEN: DELETE hace soft-delete (NO hard-delete); no aparece en listado."""
        from app.repositories.actividad_repository import ActividadRepository

        dictado_id = await _create_dictado(db_session, test_tenant.id)
        create_resp = await client.post(
            f"/api/v1/actividades/dictados/{dictado_id}",
            json={"nombre": "A_borrar", "tipo": "TP"},
        )
        actividad_id = uuid.UUID(create_resp.json()["id"])

        del_resp = await client.delete(f"/api/v1/actividades/{actividad_id}")
        assert del_resp.status_code == 204

        # Verify still in DB (soft deleted), not hard deleted
        repo = ActividadRepository(session=db_session, tenant_id=test_tenant.id)
        repo.include_deleted()
        instance = await repo.find_by_id(actividad_id)
        assert instance is not None
        assert instance.deleted_at is not None

    async def test_soft_deleted_not_in_listado(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
    ):
        """TRIANGULATE: soft-deleted no aparece en GET."""
        dictado_id = await _create_dictado(db_session, test_tenant.id)
        create_resp = await client.post(
            f"/api/v1/actividades/dictados/{dictado_id}",
            json={"nombre": "A_borrar2", "tipo": "TP"},
        )
        actividad_id = create_resp.json()["id"]
        await client.delete(f"/api/v1/actividades/{actividad_id}")

        list_resp = await client.get(f"/api/v1/actividades/dictados/{dictado_id}")
        assert all(a["id"] != actividad_id for a in list_resp.json())


class TestTenantIsolation:
    """Tenant isolation: otro tenant no accede a los datos."""

    async def test_tenant_isolation_crear(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
        another_tenant,
    ):
        """GREEN: actividad creada en otro tenant no aparece en el tenant actual."""
        # Create actividad in another_tenant
        dictado_id_otro = await _create_dictado(db_session, another_tenant.id)
        from app.services.actividad_service import ActividadService
        from app.schemas.actividades import ActividadCreate

        svc = ActividadService.create(db_session, another_tenant.id)
        await svc.crear(dictado_id_otro, ActividadCreate(nombre="TP_otro", tipo="TP"))

        # Create dictado in test_tenant — it should not see another_tenant's actividades
        dictado_id_mio = await _create_dictado(db_session, test_tenant.id)
        resp = await client.get(f"/api/v1/actividades/dictados/{dictado_id_mio}")
        assert resp.status_code == 200
        # Should be empty since no actividades were created in this tenant/dictado
        assert resp.json() == []


class TestRBAC:
    """RBAC 403 for users without permission."""

    async def test_sin_permiso_returns_403(
        self,
        app,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
        auth_user_no_perm,
    ):
        """GREEN: ALUMNO (sin actividades:gestionar) recibe 403."""
        from tests.helpers import cleanup_permission_cache as _cleanup

        async def _override_no_perm():
            return auth_user_no_perm

        app.dependency_overrides[get_current_user] = _override_no_perm
        _cleanup()
        try:
            dictado_id = await _create_dictado(db_session, test_tenant.id)
            resp = await client.post(
                f"/api/v1/actividades/dictados/{dictado_id}",
                json={"nombre": "TP_forbid", "tipo": "TP"},
            )
            assert resp.status_code == 403
        finally:
            _cleanup()

    async def test_sin_permiso_get_returns_403(
        self,
        app,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
        auth_user_no_perm,
    ):
        """TRIANGULATE: GET también requiere actividades:gestionar."""
        from tests.helpers import cleanup_permission_cache as _cleanup

        async def _override_no_perm():
            return auth_user_no_perm

        app.dependency_overrides[get_current_user] = _override_no_perm
        _cleanup()
        try:
            dictado_id = await _create_dictado(db_session, test_tenant.id)
            resp = await client.get(f"/api/v1/actividades/dictados/{dictado_id}")
            assert resp.status_code == 403
        finally:
            _cleanup()
