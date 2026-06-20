"""TDD — PROFESOR scope enforcement for avisos:publicar (C-26).

Safety net: 119 tests pass before this file was added.

Business rules:
- PROFESOR (es_propio=True) may only create avisos with alcance POR_MATERIA
  or POR_COHORTE targeting their own dictados.
- PROFESOR cannot create GLOBAL or POR_ROL avisos.
- PROFESOR cannot target a materia/cohorte they don't teach.
- COORDINADOR is unaffected (full scope).

TDD cycle:
  RED  → test written, endpoint checked → fails if scope not enforced
  GREEN → service logic enforces scope
  TRIANGULATE → multiple refusal/acceptance cases
  REFACTOR → N/A (logic already tidy)
"""

import datetime
import uuid
from datetime import UTC, datetime as dt

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.models.asignacion import Asignacion
from app.models.aviso import AlcanceAviso
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.materia import Materia
from app.models.user import User
from app.models.usuario import Usuario
from app.repositories.base import BaseRepository
from app.repositories.dictado_repository import DictadoRepository
from app.schemas.auth import CurrentUser
from tests.helpers import cleanup_permission_cache, seed_permissions_for_tenant


_JAN2026 = dt(2026, 1, 1, tzinfo=UTC)
_DEC2026 = dt(2026, 12, 31, 23, 59, 59, tzinfo=UTC)


# ── Fixtures ──────────────────────────────────────────────────────────────────


async def _create_materia_dictado(db_session, tenant_id):
    """Create carrera/materia/cohorte/dictado for a tenant. Returns (materia, cohorte, dictado)."""
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
    return materia, cohorte, dictado


@pytest.fixture
async def profesor_user(db_session, test_tenant) -> CurrentUser:
    """PROFESOR user with a vigente dictado asignacion."""
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    user = await user_repo.create(
        {
            "email": f"prof-aviso-{uuid.uuid4().hex[:6]}@test.com",
            "password_hash": "hash",
            "display_name": "Profesor Avisos",
            "is_active": True,
            "roles": ["PROFESOR"],
        }
    )
    u_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    usuario = await u_repo.create(
        {
            "user_id": user.id,
            "nombre": "Carlos",
            "apellidos": "Prof",
            "estado": "Activo",
            "facturador": False,
        }
    )
    return CurrentUser(user_id=user.id, tenant_id=test_tenant.id, roles=["PROFESOR"]), usuario


@pytest.fixture
async def coordinador_user(db_session, test_tenant) -> CurrentUser:
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    user = await user_repo.create(
        {
            "email": f"coord-aviso-{uuid.uuid4().hex[:6]}@test.com",
            "password_hash": "hash",
            "display_name": "Coordinador",
            "is_active": True,
            "roles": ["COORDINADOR"],
        }
    )
    u_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    await u_repo.create(
        {
            "user_id": user.id,
            "nombre": "Coord",
            "apellidos": "Test",
            "estado": "Activo",
            "facturador": False,
        }
    )
    return CurrentUser(user_id=user.id, tenant_id=test_tenant.id, roles=["COORDINADOR"])


@pytest.fixture(autouse=True)
async def _setup_perms(db_session, test_tenant, app, profesor_user):
    current_user, _ = profesor_user

    async def _override():
        return current_user

    app.dependency_overrides[get_current_user] = _override
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    cleanup_permission_cache()
    yield
    app.dependency_overrides.pop(get_current_user, None)
    cleanup_permission_cache()


def _aviso_payload(alcance: str, materia_id=None, cohorte_id=None):
    return {
        "alcance": alcance,
        "materia_id": str(materia_id) if materia_id else None,
        "cohorte_id": str(cohorte_id) if cohorte_id else None,
        "titulo": "Test aviso",
        "cuerpo": "Cuerpo del aviso",
        "inicio_en": _JAN2026.isoformat(),
        "fin_en": _DEC2026.isoformat(),
    }


# ── RED: PROFESOR can create aviso for own materia ────────────────────────────


class TestProfesorAvisoPorMateria:
    """GREEN: PROFESOR with a materia in their dictado can publish a POR_MATERIA aviso."""

    async def test_profesor_puede_crear_aviso_propia_materia(
        self,
        app,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
        profesor_user,
    ):
        """GREEN: PROFESOR puede publicar aviso POR_MATERIA para su materia."""
        current_user, usuario = profesor_user
        materia, cohorte, dictado = await _create_materia_dictado(db_session, test_tenant.id)

        # Assign the profesor to this dictado
        asig_repo = BaseRepository(model=Asignacion, session=db_session, tenant_id=test_tenant.id)
        await asig_repo.create(
            {
                "usuario_id": usuario.id,
                "rol": "PROFESOR",
                "dictado_id": dictado.id,
                "desde": datetime.date.today(),
                "hasta": None,
            }
        )

        resp = await client.post(
            "/api/v1/avisos",
            json=_aviso_payload(AlcanceAviso.POR_MATERIA.value, materia_id=materia.id),
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["alcance"] == "POR_MATERIA"
        assert data["materia_id"] == str(materia.id)

    async def test_profesor_no_puede_crear_aviso_global(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
        profesor_user,
    ):
        """TRIANGULATE: PROFESOR no puede crear aviso GLOBAL → 403."""
        resp = await client.post(
            "/api/v1/avisos",
            json=_aviso_payload(AlcanceAviso.GLOBAL.value),
        )
        assert resp.status_code == 403

    async def test_profesor_no_puede_crear_aviso_materia_ajena(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
        profesor_user,
    ):
        """TRIANGULATE: PROFESOR sin dictado en esa materia → 403."""
        # Create materia but do NOT assign the profesor to it
        m_repo = BaseRepository(model=Materia, session=db_session, tenant_id=test_tenant.id)
        otra_materia = await m_repo.create(
            {"codigo": f"OTRA-{uuid.uuid4().hex[:4]}", "nombre": "Otra"}
        )

        resp = await client.post(
            "/api/v1/avisos",
            json=_aviso_payload(AlcanceAviso.POR_MATERIA.value, materia_id=otra_materia.id),
        )
        assert resp.status_code == 403

    async def test_profesor_puede_crear_aviso_por_cohorte_propia(
        self,
        app,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
        profesor_user,
    ):
        """TRIANGULATE: PROFESOR puede publicar aviso POR_COHORTE para su cohorte."""
        current_user, usuario = profesor_user
        materia, cohorte, dictado = await _create_materia_dictado(db_session, test_tenant.id)

        asig_repo = BaseRepository(model=Asignacion, session=db_session, tenant_id=test_tenant.id)
        await asig_repo.create(
            {
                "usuario_id": usuario.id,
                "rol": "PROFESOR",
                "dictado_id": dictado.id,
                "desde": datetime.date.today(),
                "hasta": None,
            }
        )

        resp = await client.post(
            "/api/v1/avisos",
            json=_aviso_payload(AlcanceAviso.POR_COHORTE.value, cohorte_id=cohorte.id),
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["alcance"] == "POR_COHORTE"


class TestCoordinadorAvisoUnaffected:
    """TRIANGULATE: COORDINADOR can still create any aviso."""

    async def test_coordinador_puede_crear_aviso_global(
        self,
        app,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant,
        coordinador_user,
    ):
        """TRIANGULATE: COORDINADOR no restringido — puede crear GLOBAL aviso."""
        async def _override():
            return coordinador_user

        app.dependency_overrides[get_current_user] = _override
        cleanup_permission_cache()
        try:
            resp = await client.post(
                "/api/v1/avisos",
                json=_aviso_payload(AlcanceAviso.GLOBAL.value),
            )
            assert resp.status_code == 201
        finally:
            cleanup_permission_cache()
