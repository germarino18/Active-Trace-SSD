"""Integration tests for calificaciones router (C-10 Tasks 7.1-7.8).

Uses the `client` fixture with overridden get_current_user to bypass
auth. Seeds permissions so RBAC guards pass for the test user.
Tests cover: successful requests, permission errors, payload validation,
tenant isolation.
"""

import csv
import datetime
import io
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.models.asignacion import Asignacion
from app.models.user import User
from app.models.usuario import Usuario
from app.repositories.base import BaseRepository
from app.schemas.auth import CurrentUser
from tests.helpers import cleanup_permission_cache, seed_permissions_for_tenant


def _make_csv_bytes(headers: list[str], rows: list[list]) -> bytes:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    return output.getvalue().encode("utf-8")


async def _create_dictado_and_data(
    db_session: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID
) -> dict:
    """Create carrera, materia, cohorte, dictado, version, entradas, usuario, asignacion.

    Returns dict with all created entities.
    """
    from app.models.carrera import Carrera
    from app.models.cohorte import Cohorte
    from app.models.materia import Materia
    from app.repositories.dictado_repository import DictadoRepository
    from app.repositories.entrada_padron_repository import EntradaPadronRepository
    from app.repositories.version_padron_repository import VersionPadronRepository

    c_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=tenant_id)
    carrera = await c_repo.create({"codigo": "ING-INF", "nombre": "Ingeniería Informática"})
    m_repo = BaseRepository(model=Materia, session=db_session, tenant_id=tenant_id)
    materia = await m_repo.create({"codigo": "MAT-101", "nombre": "Análisis Matemático I"})
    co_repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=tenant_id)
    cohorte = await co_repo.create({"carrera_id": carrera.id, "nombre": "2024", "anio": 2024})
    d_repo = DictadoRepository(session=db_session, tenant_id=tenant_id)
    dictado = await d_repo.create(
        {"materia_id": materia.id, "carrera_id": carrera.id, "cohorte_id": cohorte.id}
    )

    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=tenant_id)
    existing = await usuario_repo.find_by(user_id=user_id)
    usuario = existing[0] if existing else await usuario_repo.create({
        "user_id": user_id,
        "nombre": "Test",
        "apellidos": "User",
        "estado": "Activo",
    })

    vp_repo = VersionPadronRepository(session=db_session, tenant_id=tenant_id)
    version = await vp_repo.create({
        "dictado_id": dictado.id,
        "cargado_por": usuario.id,
        "activa": True,
    })

    ep_repo = EntradaPadronRepository(session=db_session, tenant_id=tenant_id)
    entradas = await ep_repo.bulk_create([
        {"version_id": version.id, "nombre": "Juan", "apellidos": "Pérez", "email": "juan@test.com"},
        {"version_id": version.id, "nombre": "María", "apellidos": "García", "email": "maria@test.com"},
    ])

    asignacion_repo = BaseRepository(model=Asignacion, session=db_session, tenant_id=tenant_id)
    asignacion = await asignacion_repo.create({
        "usuario_id": usuario.id,
        "rol": "PROFESOR",
        "dictado_id": dictado.id,
        "desde": datetime.date.today(),
        "hasta": None,
    })

    return {
        "carrera": carrera,
        "materia": materia,
        "cohorte": cohorte,
        "dictado": dictado,
        "usuario": usuario,
        "version": version,
        "entradas": entradas,
        "asignacion": asignacion,
    }


@pytest.fixture
async def auth_user(db_session, test_tenant) -> CurrentUser:
    """Create a real User with PROFESOR role, return CurrentUser."""
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    user = await user_repo.create({
        "email": f"prof-{uuid.uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "Profesor",
        "is_active": True,
        "roles": ["PROFESOR"],
    })
    return CurrentUser(
        user_id=user.id,
        tenant_id=test_tenant.id,
        roles=["PROFESOR"],
    )


@pytest.fixture
async def auth_user_no_perm(db_session, test_tenant) -> CurrentUser:
    """User with ALUMNO role (no CALIFICACIONES permissions)."""
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


# ── Preview ──────────────────────────────────────────────────────────────


class TestPreview:
    async def test_preview_with_valid_csv_returns_200(
        self, client: AsyncClient, db_session, test_tenant, auth_user
    ):
        data = await _create_dictado_and_data(db_session, test_tenant.id, auth_user.user_id)
        csv_content = _make_csv_bytes(
            ["Apellidos", "Nombre", "Parcial 1 (Real)", "TP 1 (Real)"],
            [
                ["Pérez", "Juan", "85", "90"],
                ["García", "María", "70", "60"],
            ],
        )

        response = await client.post(
            "/api/admin/calificaciones/preview",
            files={"file": ("grades.csv", csv_content, "text/csv")},
            data={"dictado_id": str(data["dictado"].id)},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["total_filas"] == 2
        assert "preview_token" in body
        assert len(body["actividades_detectadas"]) == 2

    async def test_preview_without_perm_returns_403(
        self, client: AsyncClient, app, auth_user_no_perm
    ):
        async def _override_user():
            return auth_user_no_perm

        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()

        csv_content = _make_csv_bytes(
            ["Apellidos", "Nombre", "Parcial 1 (Real)"],
            [["Pérez", "Juan", "85"]],
        )

        response = await client.post(
            "/api/admin/calificaciones/preview",
            files={"file": ("grades.csv", csv_content, "text/csv")},
            data={"dictado_id": str(uuid.uuid4())},
        )

        assert response.status_code == 403


# ── Importar ─────────────────────────────────────────────────────────────


class TestImportar:
    async def test_importar_with_valid_preview_returns_200(
        self, client: AsyncClient, db_session, test_tenant, auth_user
    ):
        data = await _create_dictado_and_data(db_session, test_tenant.id, auth_user.user_id)
        csv_content = _make_csv_bytes(
            ["Apellidos", "Nombre", "Parcial 1 (Real)", "TP 1 (Real)"],
            [
                ["Pérez", "Juan", "85", "90"],
                ["García", "María", "70", "60"],
            ],
        )

        preview = await client.post(
            "/api/admin/calificaciones/preview",
            files={"file": ("grades.csv", csv_content, "text/csv")},
            data={"dictado_id": str(data["dictado"].id)},
        )
        assert preview.status_code == 200
        token = preview.json()["preview_token"]

        response = await client.post(
            "/api/admin/calificaciones/importar",
            json={
                "dictado_id": str(data["dictado"].id),
                "preview_token": token,
                "actividades_seleccionadas": ["Parcial 1"],
            },
        )

        assert response.status_code == 200
        body = response.json()
        assert body["total_importados"] == 2
        assert body["aprobados"] == 2  # 85 and 70 both >= 60

    async def test_importar_with_invalid_token_returns_422(
        self, client: AsyncClient
    ):
        response = await client.post(
            "/api/admin/calificaciones/importar",
            json={
                "dictado_id": str(uuid.uuid4()),
                "preview_token": "invalid-token",
                "actividades_seleccionadas": ["Parcial 1"],
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
            "/api/admin/calificaciones/importar",
            json={
                "dictado_id": str(uuid.uuid4()),
                "preview_token": "some-token",
                "actividades_seleccionadas": ["Parcial 1"],
            },
        )

        assert response.status_code == 403


# ── Preview Finalizacion ────────────────────────────────────────────────


class TestPreviewFinalizacion:
    async def test_preview_finalizacion_returns_200(
        self, client: AsyncClient, db_session, test_tenant, auth_user
    ):
        data = await _create_dictado_and_data(db_session, test_tenant.id, auth_user.user_id)
        csv_content = _make_csv_bytes(
            ["Apellidos", "Nombre", "TP 1", "TP 2"],
            [
                ["Pérez", "Juan", "Aprobado", "Entregado"],
                ["García", "María", "No aprobado", "Aprobado"],
            ],
        )

        response = await client.post(
            "/api/admin/calificaciones/preview-finalizacion",
            files={"file": ("finalizacion.csv", csv_content, "text/csv")},
            data={"dictado_id": str(data["dictado"].id)},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["total_filas"] == 2
        assert "preview_token" in body
        assert "tps_sin_calificar" in body

    async def test_preview_finalizacion_without_perm_returns_403(
        self, client: AsyncClient, app, auth_user_no_perm
    ):
        async def _override_user():
            return auth_user_no_perm

        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()

        csv_content = _make_csv_bytes(
            ["Apellidos", "Nombre", "TP 1"],
            [["Pérez", "Juan", "Aprobado"]],
        )

        response = await client.post(
            "/api/admin/calificaciones/preview-finalizacion",
            files={"file": ("finalizacion.csv", csv_content, "text/csv")},
            data={"dictado_id": str(uuid.uuid4())},
        )

        assert response.status_code == 403


# ── Importar Finalizacion ────────────────────────────────────────────────


class TestImportarFinalizacion:
    async def test_importar_finalizacion_with_invalid_token_returns_422(
        self, client: AsyncClient
    ):
        response = await client.post(
            "/api/admin/calificaciones/importar-finalizacion",
            json={
                "dictado_id": str(uuid.uuid4()),
                "preview_token": "bad-token",
                "actividades_seleccionadas": [],
            },
        )

        assert response.status_code == 422


# ── Listar Calificaciones ────────────────────────────────────────────────


class TestListarCalificaciones:
    async def test_listar_returns_200_with_empty_list(
        self, client: AsyncClient
    ):
        response = await client.get(
            f"/api/admin/calificaciones/dictados/{uuid.uuid4()}",
        )

        assert response.status_code == 200
        data = response.json()
        assert data == []

    async def test_listar_after_import_returns_imported_data(
        self, client: AsyncClient, db_session, test_tenant, auth_user
    ):
        data = await _create_dictado_and_data(db_session, test_tenant.id, auth_user.user_id)
        csv_content = _make_csv_bytes(
            ["Apellidos", "Nombre", "Parcial 1 (Real)"],
            [
                ["Pérez", "Juan", "85"],
                ["García", "María", "70"],
            ],
        )

        preview = await client.post(
            "/api/admin/calificaciones/preview",
            files={"file": ("grades.csv", csv_content, "text/csv")},
            data={"dictado_id": str(data["dictado"].id)},
        )
        token = preview.json()["preview_token"]

        await client.post(
            "/api/admin/calificaciones/importar",
            json={
                "dictado_id": str(data["dictado"].id),
                "preview_token": token,
                "actividades_seleccionadas": ["Parcial 1"],
            },
        )

        response = await client.get(
            f"/api/admin/calificaciones/dictados/{data['dictado'].id}",
        )

        assert response.status_code == 200
        body = response.json()
        assert len(body) == 2
        assert all(c["actividad"] == "Parcial 1" for c in body)
        assert all(c["aprobado"] for c in body)

    async def test_listar_without_perm_returns_403(
        self, client: AsyncClient, app, auth_user_no_perm
    ):
        async def _override_user():
            return auth_user_no_perm

        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()

        response = await client.get(
            f"/api/admin/calificaciones/dictados/{uuid.uuid4()}",
        )

        assert response.status_code == 403


# ── Umbral ────────────────────────────────────────────────────────────────


class TestUmbral:
    async def test_get_umbral_returns_defaults(
        self, client: AsyncClient
    ):
        response = await client.get(
            "/api/admin/calificaciones/umbral",
            params={"dictado_id": str(uuid.uuid4())},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["umbral_pct"] == 60
        assert body["es_default"] is True

    async def test_put_umbral_returns_200(
        self, client: AsyncClient, db_session, test_tenant, auth_user
    ):
        data = await _create_dictado_and_data(db_session, test_tenant.id, auth_user.user_id)

        response = await client.put(
            "/api/admin/calificaciones/umbral",
            json={
                "dictado_id": str(data["dictado"].id),
                "umbral_pct": 75,
                "valores_aprobatorios": ["Satisfactorio"],
            },
        )

        assert response.status_code == 200
        body = response.json()
        assert body["umbral_pct"] == 75
        assert body["valores_aprobatorios"] == ["Satisfactorio"]
        assert body["calificaciones_recalculadas"] >= 0

    async def test_get_umbral_after_put_returns_configured_values(
        self, client: AsyncClient, db_session, test_tenant, auth_user
    ):
        data = await _create_dictado_and_data(db_session, test_tenant.id, auth_user.user_id)

        await client.put(
            "/api/admin/calificaciones/umbral",
            json={
                "dictado_id": str(data["dictado"].id),
                "umbral_pct": 80,
            },
        )

        response = await client.get(
            "/api/admin/calificaciones/umbral",
            params={"dictado_id": str(data["dictado"].id)},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["umbral_pct"] == 80
        assert body["es_default"] is False

    async def test_put_umbral_with_invalid_pct_returns_422(
        self, client: AsyncClient
    ):
        response = await client.put(
            "/api/admin/calificaciones/umbral",
            json={
                "dictado_id": str(uuid.uuid4()),
                "umbral_pct": 150,
            },
        )

        assert response.status_code == 422

    async def test_put_umbral_without_perm_returns_403(
        self, client: AsyncClient, app, auth_user_no_perm
    ):
        async def _override_user():
            return auth_user_no_perm

        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()

        response = await client.put(
            "/api/admin/calificaciones/umbral",
            json={
                "dictado_id": str(uuid.uuid4()),
                "umbral_pct": 60,
            },
        )

        assert response.status_code == 403


# ── Tenant Isolation ──────────────────────────────────────────────────────


class TestTenantIsolation:
    async def test_another_tenant_cannot_see_dictado_data(
        self, client: AsyncClient, db_session, test_tenant, another_tenant, auth_user
    ):
        """Data from test_tenant should be invisible when using another_tenant's identity."""
        data = await _create_dictado_and_data(db_session, test_tenant.id, auth_user.user_id)

        user_repo = BaseRepository(model=User, session=db_session, tenant_id=another_tenant.id)
        other_user = await user_repo.create({
            "email": f"other-{uuid.uuid4().hex[:8]}@test.com",
            "password_hash": "hash",
            "display_name": "Other",
            "is_active": True,
            "roles": ["PROFESOR"],
        })
        other_current_user = CurrentUser(
            user_id=other_user.id,
            tenant_id=another_tenant.id,
            roles=["PROFESOR"],
        )

        async def _override_user():
            return other_current_user

        app = client._transport.app
        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()

        await seed_permissions_for_tenant(db_session, another_tenant.id)

        response = await client.get(
            f"/api/admin/calificaciones/dictados/{data['dictado'].id}",
        )

        assert response.status_code == 200
        body = response.json()
        assert body == []
