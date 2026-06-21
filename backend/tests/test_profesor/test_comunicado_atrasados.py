"""TDD — comunicado-atrasados endpoint and atrasados subtipo verification (C-26).

New endpoint:
  POST /api/v1/profesor/dictados/{dictado_id}/comunicado-atrasados
    body: {actividad_id, subtipo: 'desaprobado'|'atrasado_null', asunto_template, cuerpo_template}

Also verifies that GET /atrasados returns items with estado and subtipo fields.

Safety net: 50 + 69 + new = baseline before this file was added.

TDD cycle:
  RED  → tests written before implementation
  GREEN → service + router methods added
  TRIANGULATE → subtipo='desaprobado', tenant isolation, no recipients case
"""

import datetime
import decimal
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

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


# ── Fixtures and helpers ──────────────────────────────────────────────────────


async def _setup_dictado(db_session, tenant_id, user_id):
    """Create a full dictado with padrón entries and PROFESOR asignacion."""
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
    ep1 = await ep_repo.create(
        {
            "version_id": version.id,
            "nombre": "Alumno0",
            "apellidos": "Test",
            "email": "alumno0@test.com",
        }
    )
    ep2 = await ep_repo.create(
        {
            "version_id": version.id,
            "nombre": "Alumno1",
            "apellidos": "Test",
            "email": "alumno1@test.com",
        }
    )

    return dictado, version, [ep1, ep2]


@pytest.fixture
async def auth_user(db_session, test_tenant) -> CurrentUser:
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    user = await user_repo.create(
        {
            "email": f"prof-com-{uuid.uuid4().hex[:8]}@test.com",
            "password_hash": "hash",
            "display_name": "Profesor Com",
            "is_active": True,
            "roles": ["PROFESOR"],
        }
    )
    return CurrentUser(user_id=user.id, tenant_id=test_tenant.id, roles=["PROFESOR"])


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


# ── §7: atrasados endpoint returns estado and subtipo ────────────────────────


class TestAtrasadosSubtipo:
    """GREEN: atrasados endpoint returns items with estado and subtipo."""

    async def test_atrasados_retorna_estado_y_subtipo(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
        auth_user,
    ):
        """GREEN: GET /atrasados devuelve items con estado y subtipo."""
        dictado, version, entradas = await _setup_dictado(
            db_session, test_tenant.id, auth_user.user_id
        )

        resp = await client.get(
            f"/api/v1/profesor/dictados/{dictado.id}/atrasados"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        for item in data:
            assert "estado" in item
            assert "subtipo" in item

    async def test_desaprobado_tiene_subtipo_desaprobado(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
        auth_user,
    ):
        """TRIANGULATE: alumno con nota < umbral tiene subtipo='desaprobado'."""
        dictado, version, entradas = await _setup_dictado(
            db_session, test_tenant.id, auth_user.user_id
        )
        # Create Actividad via API
        act_resp = await client.post(
            f"/api/v1/actividades/dictados/{dictado.id}",
            json={"nombre": "TP1-sub", "tipo": "TP", "fecha_limite": "2026-07-01"},
        )
        assert act_resp.status_code == 201

        # Seed desaprobada calificacion for alumno0
        calif_repo = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
        await calif_repo.create(
            {
                "entrada_padron_id": entradas[0].id,
                "dictado_id": dictado.id,
                "actividad": "TP1-sub",
                "nota_numerica": 30.0,  # below 60 default threshold
                "aprobado": False,
                "origen": "Manual",
            }
        )

        resp = await client.get(f"/api/v1/profesor/dictados/{dictado.id}/atrasados")
        assert resp.status_code == 200
        items = {str(i["alumno_id"]): i for i in resp.json()}
        alumno0 = items[str(entradas[0].id)]
        assert alumno0["estado"] == "atrasado"
        assert alumno0["subtipo"] == "desaprobado"

    async def test_atrasado_null_tiene_subtipo_atrasado_null(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
        auth_user,
    ):
        """TRIANGULATE: faltante con fecha_limite vencida tiene subtipo='atrasado_null'."""
        dictado, version, entradas = await _setup_dictado(
            db_session, test_tenant.id, auth_user.user_id
        )
        # Actividad with past fecha_limite → no calificacion → atrasado_null
        await client.post(
            f"/api/v1/actividades/dictados/{dictado.id}",
            json={"nombre": "TP-vencido", "tipo": "TP", "fecha_limite": "2020-01-01"},
        )

        resp = await client.get(f"/api/v1/profesor/dictados/{dictado.id}/atrasados")
        assert resp.status_code == 200
        for item in resp.json():
            assert item["estado"] == "atrasado"
            assert item["subtipo"] == "atrasado_null"


# ── §8b: comunicado-atrasados endpoint ────────────────────────────────────────


class TestComunicadoAtrasados:
    """GREEN → TRIANGULATE: POST /comunicado-atrasados targets correct recipients."""

    async def _create_actividad_and_desaprobado(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        tenant_id: uuid.UUID,
        dictado,
        entradas,
        nombre: str = "TP-DESP",
    ):
        """Create actividad and seed a desaprobada calificacion for entradas[0]."""
        act_resp = await client.post(
            f"/api/v1/actividades/dictados/{dictado.id}",
            json={"nombre": nombre, "tipo": "TP", "fecha_limite": "2026-07-01"},
        )
        assert act_resp.status_code == 201
        act = act_resp.json()

        calif_repo = CalificacionRepository(session=db_session, tenant_id=tenant_id)
        await calif_repo.create(
            {
                "entrada_padron_id": entradas[0].id,
                "dictado_id": dictado.id,
                "actividad": nombre,
                "nota_numerica": 20.0,  # clearly below threshold
                "aprobado": False,
                "origen": "Manual",
            }
        )
        return act

    async def test_comunicado_desaprobado_targets_desaprobados(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
        auth_user,
    ):
        """GREEN: comunicado subtipo=desaprobado → total > 0, lote_id set."""
        dictado, version, entradas = await _setup_dictado(
            db_session, test_tenant.id, auth_user.user_id
        )
        act = await self._create_actividad_and_desaprobado(
            client, db_session, test_tenant.id, dictado, entradas, "TP-D1"
        )

        resp = await client.post(
            f"/api/v1/profesor/dictados/{dictado.id}/comunicado-atrasados",
            json={
                "actividad_id": act["id"],
                "subtipo": "desaprobado",
                "asunto_template": "Alerta desaprobado {nombre}",
                "cuerpo_template": "Tenés la actividad {actividad} desaprobada.",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        # alumno0 has email so at least 1 recipient
        assert data["total"] >= 1
        assert data["lote_id"] is not None

    async def test_comunicado_atrasado_null_targets_faltantes(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
        auth_user,
    ):
        """TRIANGULATE: subtipo=atrasado_null targets alumnos sin calificacion y vencidos."""
        dictado, version, entradas = await _setup_dictado(
            db_session, test_tenant.id, auth_user.user_id
        )
        # Actividad with past fecha_limite → entradas[0] and entradas[1] both null
        act_resp = await client.post(
            f"/api/v1/actividades/dictados/{dictado.id}",
            json={"nombre": "TP-NULL", "tipo": "TP", "fecha_limite": "2020-01-01"},
        )
        act = act_resp.json()

        resp = await client.post(
            f"/api/v1/profesor/dictados/{dictado.id}/comunicado-atrasados",
            json={
                "actividad_id": act["id"],
                "subtipo": "atrasado_null",
                "asunto_template": "Faltante {nombre}",
                "cuerpo_template": "Falta entrega {actividad}.",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        # Both entradas have email set → both are recipients
        assert data["total"] == 2

    async def test_comunicado_dictado_otro_tenant_404(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
        another_tenant,
        auth_user,
    ):
        """TRIANGULATE: dictado de otro tenant → 404 (tenant isolation)."""
        dictado_otro, _, entradas_otro = await _setup_dictado(
            db_session, another_tenant.id, auth_user.user_id
        )
        # Create actividad in the other tenant
        from app.services.actividad_service import ActividadService
        from app.schemas.actividades import ActividadCreate
        svc = ActividadService.create(db_session, another_tenant.id)
        act_otro = await svc.crear(
            dictado_otro.id, ActividadCreate(nombre="TP-otro", tipo="TP")
        )

        resp = await client.post(
            f"/api/v1/profesor/dictados/{dictado_otro.id}/comunicado-atrasados",
            json={
                "actividad_id": str(act_otro.id),
                "subtipo": "desaprobado",
                "asunto_template": "test",
                "cuerpo_template": "test body",
            },
        )
        assert resp.status_code == 404

    async def test_comunicado_sin_destinatarios_retorna_cero(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
        auth_user,
    ):
        """TRIANGULATE: sin alumnos en subtipo → total=0, lote_id=null."""
        dictado, version, entradas = await _setup_dictado(
            db_session, test_tenant.id, auth_user.user_id
        )
        # Actividad with past fecha_limite, but all alumnos have nota APPROVED
        act_resp = await client.post(
            f"/api/v1/actividades/dictados/{dictado.id}",
            json={"nombre": "TP-ALL-OK", "tipo": "TP", "fecha_limite": "2020-01-01"},
        )
        act = act_resp.json()

        # Seed aprobadas for all entradas
        calif_repo = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
        for ep in entradas:
            await calif_repo.create(
                {
                    "entrada_padron_id": ep.id,
                    "dictado_id": dictado.id,
                    "actividad": "TP-ALL-OK",
                    "nota_numerica": 90.0,
                    "aprobado": True,
                    "origen": "Manual",
                }
            )

        resp = await client.post(
            f"/api/v1/profesor/dictados/{dictado.id}/comunicado-atrasados",
            json={
                "actividad_id": act["id"],
                "subtipo": "desaprobado",
                "asunto_template": "test",
                "cuerpo_template": "test body",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["lote_id"] is None

    async def test_comunicado_subtipo_invalido_422(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
        auth_user,
    ):
        """TRIANGULATE: subtipo inválido → 422 (Pydantic pattern validation)."""
        dictado, version, entradas = await _setup_dictado(
            db_session, test_tenant.id, auth_user.user_id
        )
        fake_act_id = uuid.uuid4()
        resp = await client.post(
            f"/api/v1/profesor/dictados/{dictado.id}/comunicado-atrasados",
            json={
                "actividad_id": str(fake_act_id),
                "subtipo": "invalido",
                "asunto_template": "test",
                "cuerpo_template": "body",
            },
        )
        assert resp.status_code == 422
