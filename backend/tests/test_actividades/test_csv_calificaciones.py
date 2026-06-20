"""TDD — CSV template and CSV upload endpoints for actividades (C-26).

New endpoints:
  GET  /api/v1/actividades/{actividad_id}/plantilla-csv
  POST /api/v1/actividades/{actividad_id}/calificaciones-csv

Safety net: 50 + 69 = 119 tests passed before this file was added.

TDD cycle:
  RED  → write test first (endpoint doesn't exist yet)
  GREEN → implement minimum code to pass
  TRIANGULATE → multiple scenarios per behavior
  REFACTOR → clean up
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
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.entrada_padron import EntradaPadron
from app.models.materia import Materia
from app.models.user import User
from app.models.usuario import Usuario
from app.models.version_padron import VersionPadron
from app.repositories.base import BaseRepository
from app.repositories.calificacion_repository import CalificacionRepository
from app.repositories.dictado_repository import DictadoRepository
from app.schemas.auth import CurrentUser
from tests.helpers import cleanup_permission_cache, seed_permissions_for_tenant


# ── Shared setup ──────────────────────────────────────────────────────────────


async def _create_dictado_with_padron(db_session, tenant_id, user_id):
    """Create carrera/materia/cohorte/dictado/version/entradas for tests."""
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

    u_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=tenant_id)
    existing = await u_repo.find_by(user_id=user_id)
    usuario = existing[0] if existing else await u_repo.create(
        {"user_id": user_id, "nombre": "Profe", "apellidos": "Test", "estado": "Activo", "facturador": False}
    )

    asig_repo = BaseRepository(model=Asignacion, session=db_session, tenant_id=tenant_id)
    await asig_repo.create(
        {
            "usuario_id": usuario.id,
            "rol": "PROFESOR",
            "dictado_id": dictado.id,
            "desde": datetime.date.today(),
            "hasta": None,
        }
    )

    vp_repo = BaseRepository(model=VersionPadron, session=db_session, tenant_id=tenant_id)
    version = await vp_repo.create(
        {"dictado_id": dictado.id, "cargado_por": usuario.id, "activa": True}
    )

    ep_repo = BaseRepository(model=EntradaPadron, session=db_session, tenant_id=tenant_id)
    entradas = []
    for i in range(3):
        ep = await ep_repo.create(
            {
                "version_id": version.id,
                "nombre": f"Alumno{i}",
                "apellidos": "Test",
                "email": f"alumno{i}@test.com",
            }
        )
        entradas.append(ep)

    return dictado, version, entradas


async def _create_actividad(client: AsyncClient, dictado_id: uuid.UUID, nombre: str = "TP1"):
    """Helper: POST to create an Actividad via the API."""
    resp = await client.post(
        f"/api/v1/actividades/dictados/{dictado_id}",
        json={"nombre": nombre, "tipo": "TP", "fecha_limite": "2026-07-01"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
async def auth_user(db_session, test_tenant) -> CurrentUser:
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    user = await user_repo.create(
        {
            "email": f"prof-csv-{uuid.uuid4().hex[:8]}@test.com",
            "password_hash": "hash",
            "display_name": "Profesor CSV",
            "is_active": True,
            "roles": ["PROFESOR"],
        }
    )
    return CurrentUser(user_id=user.id, tenant_id=test_tenant.id, roles=["PROFESOR"])


@pytest.fixture
async def auth_user_alumno(db_session, test_tenant) -> CurrentUser:
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
    async def _override():
        return auth_user

    app.dependency_overrides[get_current_user] = _override
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    cleanup_permission_cache()
    yield
    app.dependency_overrides.pop(get_current_user, None)
    cleanup_permission_cache()


# ── GET /plantilla-csv ────────────────────────────────────────────────────────


class TestPlantillaCSV:
    """RED → GREEN: GET plantilla-csv returns CSV with padrón alumnos."""

    async def test_plantilla_csv_retorna_alumnos(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
        auth_user,
    ):
        """GREEN: plantilla incluye todas las entradas del padrón activo."""
        dictado, version, entradas = await _create_dictado_with_padron(
            db_session, test_tenant.id, auth_user.user_id
        )
        act = await _create_actividad(client, dictado.id)

        resp = await client.get(f"/api/v1/actividades/{act['id']}/plantilla-csv")
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]

        body = resp.text
        reader = csv.DictReader(io.StringIO(body))
        rows = list(reader)

        # Must have one row per entrada (3 alumnos)
        assert len(rows) == 3
        # Verify columns
        assert "entrada_padron_id" in reader.fieldnames
        assert "nombre" in reader.fieldnames
        assert "nota" in reader.fieldnames
        assert "aprobado" in reader.fieldnames

    async def test_plantilla_csv_nota_y_aprobado_vacios(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
        auth_user,
    ):
        """TRIANGULATE: nota y aprobado están vacíos en la plantilla."""
        dictado, version, entradas = await _create_dictado_with_padron(
            db_session, test_tenant.id, auth_user.user_id
        )
        act = await _create_actividad(client, dictado.id)

        resp = await client.get(f"/api/v1/actividades/{act['id']}/plantilla-csv")
        rows = list(csv.DictReader(io.StringIO(resp.text)))
        for row in rows:
            assert row["nota"] == ""
            assert row["aprobado"] == ""

    async def test_plantilla_csv_actividad_inexistente_404(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
        auth_user,
    ):
        """TRIANGULATE: actividad de otro tenant → 404."""
        # Use a UUID that doesn't exist in this tenant
        fake_id = uuid.uuid4()
        resp = await client.get(f"/api/v1/actividades/{fake_id}/plantilla-csv")
        assert resp.status_code == 404

    async def test_plantilla_csv_content_disposition_attachment(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
        auth_user,
    ):
        """TRIANGULATE: Content-Disposition is attachment."""
        dictado, version, entradas = await _create_dictado_with_padron(
            db_session, test_tenant.id, auth_user.user_id
        )
        act = await _create_actividad(client, dictado.id)

        resp = await client.get(f"/api/v1/actividades/{act['id']}/plantilla-csv")
        assert resp.status_code == 200
        cd = resp.headers.get("content-disposition", "")
        assert "attachment" in cd


# ── POST /calificaciones-csv ──────────────────────────────────────────────────


class TestCalificacionesCSVUpload:
    """RED → GREEN → TRIANGULATE: POST calificaciones-csv upserts Calificaciones."""

    def _build_csv(self, rows: list[dict]) -> bytes:
        """Build a CSV bytes payload from rows."""
        output = io.StringIO()
        if rows:
            fieldnames = list(rows[0].keys())
        else:
            fieldnames = ["entrada_padron_id", "usuario_id", "nombre", "apellido", "nota", "aprobado"]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        return output.getvalue().encode("utf-8")

    async def test_upload_csv_crea_calificaciones(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
        auth_user,
    ):
        """GREEN: upload CSV crea Calificaciones con nota y aprobado correctos."""
        dictado, version, entradas = await _create_dictado_with_padron(
            db_session, test_tenant.id, auth_user.user_id
        )
        act = await _create_actividad(client, dictado.id, nombre="TP-CSV")

        csv_rows = [
            {
                "entrada_padron_id": str(entradas[0].id),
                "usuario_id": "",
                "nombre": "Alumno0",
                "apellido": "Test",
                "nota": "8.5",
                "aprobado": "true",
            },
            {
                "entrada_padron_id": str(entradas[1].id),
                "usuario_id": "",
                "nombre": "Alumno1",
                "apellido": "Test",
                "nota": "4.0",
                "aprobado": "false",
            },
        ]
        csv_content = self._build_csv(csv_rows)

        resp = await client.post(
            f"/api/v1/actividades/{act['id']}/calificaciones-csv",
            files={"file": ("notas.csv", csv_content, "text/csv")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["created"] == 2
        assert data["updated"] == 0
        assert data["total"] == 2

        # Verify Calificaciones in DB
        actividad_id = uuid.UUID(act["id"])
        calif_repo = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
        califs = await calif_repo.find_by_dictado(dictado.id)
        linked = [c for c in califs if c.actividad_id == actividad_id]
        assert len(linked) == 2

        by_ep = {str(c.entrada_padron_id): c for c in linked}
        assert float(by_ep[str(entradas[0].id)].nota_numerica) == 8.5
        assert by_ep[str(entradas[0].id)].aprobado is True
        assert float(by_ep[str(entradas[1].id)].nota_numerica) == 4.0
        assert by_ep[str(entradas[1].id)].aprobado is False

    async def test_upload_csv_reupsert_actualiza(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
        auth_user,
    ):
        """TRIANGULATE: re-upload actualiza (upsert), no duplica."""
        dictado, version, entradas = await _create_dictado_with_padron(
            db_session, test_tenant.id, auth_user.user_id
        )
        act = await _create_actividad(client, dictado.id, nombre="TP-UPSERT")
        actividad_id = uuid.UUID(act["id"])

        csv_rows = [
            {
                "entrada_padron_id": str(entradas[0].id),
                "usuario_id": "",
                "nombre": "Alumno0",
                "apellido": "Test",
                "nota": "5.0",
                "aprobado": "false",
            }
        ]
        # First upload
        await client.post(
            f"/api/v1/actividades/{actividad_id}/calificaciones-csv",
            files={"file": ("notas.csv", self._build_csv(csv_rows), "text/csv")},
        )

        # Second upload with updated nota
        csv_rows[0]["nota"] = "9.0"
        csv_rows[0]["aprobado"] = "true"
        resp2 = await client.post(
            f"/api/v1/actividades/{actividad_id}/calificaciones-csv",
            files={"file": ("notas2.csv", self._build_csv(csv_rows), "text/csv")},
        )
        assert resp2.status_code == 200
        data = resp2.json()
        assert data["updated"] == 1
        assert data["created"] == 0

        # Verify only ONE calificacion in DB for this (entrada, actividad)
        calif_repo = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
        califs = await calif_repo.find_by_dictado(dictado.id)
        linked = [c for c in califs if c.actividad_id == actividad_id]
        assert len(linked) == 1
        assert float(linked[0].nota_numerica) == 9.0
        assert linked[0].aprobado is True

    async def test_upload_csv_otro_tenant_404(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
        another_tenant,
        auth_user,
    ):
        """TRIANGULATE: actividad de otro tenant → 404 (tenant isolation)."""
        from app.services.actividad_service import ActividadService
        from app.schemas.actividades import ActividadCreate

        # Create dictado and actividad in another_tenant
        dictado_otro, _, _ = await _create_dictado_with_padron(
            db_session, another_tenant.id, auth_user.user_id
        )
        svc = ActividadService.create(db_session, another_tenant.id)
        act_otro = await svc.crear(
            dictado_otro.id,
            ActividadCreate(nombre="TP-otro", tipo="TP"),
        )

        csv_content = self._build_csv([])
        resp = await client.post(
            f"/api/v1/actividades/{act_otro.id}/calificaciones-csv",
            files={"file": ("notas.csv", csv_content, "text/csv")},
        )
        assert resp.status_code == 404

    async def test_upload_csv_malformed_422(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
        auth_user,
    ):
        """TRIANGULATE: CSV sin columna requerida → 422."""
        dictado, version, entradas = await _create_dictado_with_padron(
            db_session, test_tenant.id, auth_user.user_id
        )
        act = await _create_actividad(client, dictado.id, nombre="TP-422")

        # Missing 'nota' and 'aprobado' columns
        bad_csv = b"entrada_padron_id,nombre\nabc,Alumno\n"
        resp = await client.post(
            f"/api/v1/actividades/{act['id']}/calificaciones-csv",
            files={"file": ("bad.csv", bad_csv, "text/csv")},
        )
        assert resp.status_code == 422

    async def test_upload_csv_actividad_id_en_calificacion(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
        auth_user,
    ):
        """TRIANGULATE: Calificacion creada tiene actividad_id y actividad nombre correctos."""
        dictado, version, entradas = await _create_dictado_with_padron(
            db_session, test_tenant.id, auth_user.user_id
        )
        act = await _create_actividad(client, dictado.id, nombre="TP-LINKED")
        actividad_id = uuid.UUID(act["id"])

        csv_rows = [
            {
                "entrada_padron_id": str(entradas[0].id),
                "usuario_id": "",
                "nombre": "Alumno0",
                "apellido": "Test",
                "nota": "7.5",
                "aprobado": "true",
            }
        ]
        await client.post(
            f"/api/v1/actividades/{actividad_id}/calificaciones-csv",
            files={"file": ("notas.csv", self._build_csv(csv_rows), "text/csv")},
        )

        calif_repo = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
        califs = await calif_repo.find_by_dictado(dictado.id)
        linked = [c for c in califs if c.actividad_id == actividad_id]
        assert len(linked) == 1
        assert linked[0].actividad == "TP-LINKED"
        assert linked[0].origen == "Importado"
