"""Integration tests for the alumno dashboard endpoint."""

from datetime import UTC, datetime, timedelta

from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.models.aviso import Aviso, AlcanceAviso, SeveridadAviso
from app.models.calificacion import Calificacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.dictado import Dictado
from app.models.entrada_padron import EntradaPadron
from app.models.evaluacion import Evaluacion
from app.models.materia import Materia
from app.models.tenant import Tenant
from app.models.user import User
from app.models.usuario import Usuario
from app.models.version_padron import VersionPadron
from app.repositories.base import BaseRepository
from app.schemas.auth import CurrentUser
from tests.helpers import cleanup_permission_cache, seed_permissions_for_tenant


# ── Fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture
async def auth_user(db_session, test_tenant) -> tuple[CurrentUser, UUID]:
    """User with ALUMNO role (has estado-academico:ver)."""
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    user = await user_repo.create({
        "email": f"alumno-{uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "Alumno Test",
        "is_active": True,
    })
    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    usuario = await usuario_repo.create({
        "user_id": user.id,
        "nombre": "Alumno",
        "apellidos": "Test",
    })
    return CurrentUser(
        user_id=user.id,
        tenant_id=test_tenant.id,
        roles=["ALUMNO"],
    ), usuario.id


@pytest.fixture
async def auth_user_no_perm(db_session, test_tenant) -> CurrentUser:
    """User without estado-academico:ver (NEXO role)."""
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    user = await user_repo.create({
        "email": f"nexo-{uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "Nexo Test",
        "is_active": True,
    })
    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    await usuario_repo.create({
        "user_id": user.id,
        "nombre": "Nexo",
        "apellidos": "Test",
    })
    return CurrentUser(
        user_id=user.id,
        tenant_id=test_tenant.id,
        roles=["NEXO"],
    )


@pytest.fixture(autouse=True)
async def _setup_auth(app, db_session, test_tenant, auth_user):
    async def _override_user():
        return auth_user[0]

    app.dependency_overrides[get_current_user] = _override_user
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    cleanup_permission_cache()
    yield
    app.dependency_overrides.pop(get_current_user, None)
    cleanup_permission_cache()


@pytest.fixture
async def seed_basic_dashboard_data(
    db_session: AsyncSession,
    test_tenant: Tenant,
    auth_user,
) -> dict:
    """Seed materias, avisos, evaluaciones and fechas for the alumno dashboard."""
    _current_user, usuario_id = auth_user

    # Create Materia + Dictado
    materia_repo = BaseRepository(model=Materia, session=db_session, tenant_id=test_tenant.id)
    materia = await materia_repo.create({
        "codigo": "MATE101",
        "nombre": "Matemáticas I",
    })

    carrera_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=test_tenant.id)
    carrera = await carrera_repo.create({
        "codigo": "ING",
        "nombre": "Ingeniería",
    })

    cohorte_repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=test_tenant.id)
    cohorte = await cohorte_repo.create({
        "carrera_id": carrera.id,
        "nombre": "2024",
    })

    dictado_repo = BaseRepository(model=Dictado, session=db_session, tenant_id=test_tenant.id)
    dictado = await dictado_repo.create({
        "materia_id": materia.id,
        "carrera_id": carrera.id,
        "cohorte_id": cohorte.id,
        "estado": "Activo",
    })

    # Create VersionPadron + EntradaPadron linking usuario to dictado
    version_repo = BaseRepository(model=VersionPadron, session=db_session, tenant_id=test_tenant.id)
    version = await version_repo.create({
        "dictado_id": dictado.id,
        "cargado_por": usuario_id,
        "activa": True,
    })

    entrada_repo = BaseRepository(model=EntradaPadron, session=db_session, tenant_id=test_tenant.id)
    entrada = await entrada_repo.create({
        "version_id": version.id,
        "usuario_id": usuario_id,
        "nombre": "Alumno",
        "apellidos": "Test",
    })

    # Create Calificaciones for progress
    calif_repo = BaseRepository(model=Calificacion, session=db_session, tenant_id=test_tenant.id)
    await calif_repo.create({
        "entrada_padron_id": entrada.id,
        "dictado_id": dictado.id,
        "actividad": "Parcial 1",
        "nota_numerica": 8.5,
        "aprobado": True,
    })
    await calif_repo.create({
        "entrada_padron_id": entrada.id,
        "dictado_id": dictado.id,
        "actividad": "TP 1",
        "nota_numerica": 7.0,
        "aprobado": True,
    })

    # Create an unread aviso (one that requires ack and has not been ack'd)
    aviso_repo = BaseRepository(model=Aviso, session=db_session, tenant_id=test_tenant.id)
    now = datetime.now(UTC)
    await aviso_repo.create({
        "alcance": AlcanceAviso.GLOBAL.value,
        "severidad": SeveridadAviso.INFO.value,
        "titulo": "Aviso importante",
        "cuerpo": "Este aviso requiere confirmación",
        "inicio_en": now - timedelta(days=1),
        "fin_en": now + timedelta(days=30),
        "activo": True,
        "requiere_ack": True,
    })

    # Create an upcoming coloquio
    ev_repo = BaseRepository(model=Evaluacion, session=db_session, tenant_id=test_tenant.id)
    evaluacion = await ev_repo.create({
        "dictado_id": dictado.id,
        "tipo": "Coloquio",
        "instancia": "Coloquio Final",
        "dias_disponibles": 10,
        "cupo_maximo": 30,
        "estado": "Activa",
    })

    # Create a reservation so the alumno sees this coloquio
    from app.models.reserva_evaluacion import ReservaEvaluacion
    reserva_repo = BaseRepository(model=ReservaEvaluacion, session=db_session, tenant_id=test_tenant.id)
    await reserva_repo.create({
        "evaluacion_id": evaluacion.id,
        "alumno_id": usuario_id,
        "fecha_hora": datetime.now(UTC) + timedelta(days=7),
        "estado": "Activa",
    })

    return {
        "materia_id": materia.id,
        "dictado_id": dictado.id,
        "evaluacion_id": evaluacion.id,
    }


# ── Tests ─────────────────────────────────────────────────────────────────


class TestAlumnoDashboard:
    async def test_dashboard_returns_200_and_correct_shape(
        self,
        client: AsyncClient,
        seed_basic_dashboard_data,
    ):
        response = await client.get("/api/v1/alumno/dashboard")
        assert response.status_code == 200
        body = response.json()

        # Validate response shape
        assert "materias" in body
        assert "avisos_no_leidos" in body
        assert "comunicaciones_no_leidas" in body
        assert "proximos_coloquios" in body
        assert "proximas_fechas" in body

        # Should have at least 1 materia
        assert len(body["materias"]) >= 1
        materia = body["materias"][0]
        assert materia["nombre"] == "Matemáticas I"
        assert materia["progreso"]["total"] >= 2
        assert materia["progreso"]["aprobadas"] >= 2

        # Should have at least 1 pending aviso
        assert body["avisos_no_leidos"] >= 1

        # Should have the upcoming coloquio
        assert len(body["proximos_coloquios"]) >= 1

    async def test_dashboard_403_if_user_lacks_permission(
        self,
        client: AsyncClient,
        app,
        db_session,
        test_tenant,
        auth_user_no_perm,
    ):
        async def _override_user():
            return auth_user_no_perm

        app.dependency_overrides[get_current_user] = _override_user
        cleanup_permission_cache()

        response = await client.get("/api/v1/alumno/dashboard")
        assert response.status_code == 403

    async def test_dashboard_multi_tenant_isolation(
        self,
        client: AsyncClient,
        app,
        db_session: AsyncSession,
        test_tenant: Tenant,
        another_tenant: Tenant,
    ):
        """User in tenant A should not see tenant B's dashboard data."""
        # Create user in Tenant A (test_tenant)
        user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
        user_a = await user_repo.create({
            "email": f"alumno-a-{uuid4().hex[:8]}@test.com",
            "password_hash": "hash",
            "display_name": "Alumno A",
            "is_active": True,
        })
        usuario_repo_a = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
        usuario_a = await usuario_repo_a.create({
            "user_id": user_a.id,
            "nombre": "Alumno",
            "apellidos": "A",
        })
        auth_user_a = CurrentUser(
            user_id=user_a.id,
            tenant_id=test_tenant.id,
            roles=["ALUMNO"],
        )

        # Create user in Tenant B (another_tenant)
        user_repo_b = BaseRepository(model=User, session=db_session, tenant_id=another_tenant.id)
        user_b = await user_repo_b.create({
            "email": f"alumno-b-{uuid4().hex[:8]}@test.com",
            "password_hash": "hash",
            "display_name": "Alumno B",
            "is_active": True,
        })
        usuario_repo_b = BaseRepository(model=Usuario, session=db_session, tenant_id=another_tenant.id)
        usuario_b = await usuario_repo_b.create({
            "user_id": user_b.id,
            "nombre": "Alumno",
            "apellidos": "B",
        })

        # Seed permissions for both tenants
        await seed_permissions_for_tenant(db_session, test_tenant.id)
        await seed_permissions_for_tenant(db_session, another_tenant.id)
        cleanup_permission_cache()

        # Seed a materia/entrada in Tenant B only
        materia_repo_b = BaseRepository(model=Materia, session=db_session, tenant_id=another_tenant.id)
        materia_b = await materia_repo_b.create({
            "codigo": "FIS101",
            "nombre": "Física I",
        })
        carrera_repo_b = BaseRepository(model=Carrera, session=db_session, tenant_id=another_tenant.id)
        carrera_b = await carrera_repo_b.create({
            "codigo": "ING",
            "nombre": "Ingeniería",
        })
        cohorte_repo_b = BaseRepository(model=Cohorte, session=db_session, tenant_id=another_tenant.id)
        cohorte_b = await cohorte_repo_b.create({
            "carrera_id": carrera_b.id,
            "nombre": "2024",
        })
        dictado_repo_b = BaseRepository(model=Dictado, session=db_session, tenant_id=another_tenant.id)
        dictado_b = await dictado_repo_b.create({
            "materia_id": materia_b.id,
            "carrera_id": carrera_b.id,
            "cohorte_id": cohorte_b.id,
            "estado": "Activo",
        })
        version_repo_b = BaseRepository(model=VersionPadron, session=db_session, tenant_id=another_tenant.id)
        version_b = await version_repo_b.create({
            "dictado_id": dictado_b.id,
            "cargado_por": usuario_b.id,
            "activa": True,
        })
        entrada_repo_b = BaseRepository(model=EntradaPadron, session=db_session, tenant_id=another_tenant.id)
        await entrada_repo_b.create({
            "version_id": version_b.id,
            "usuario_id": usuario_b.id,
            "nombre": "Alumno",
            "apellidos": "B",
        })

        # Authenticate as Tenant A user and verify tenant B data is NOT visible
        async def _override_user_a():
            return auth_user_a

        app.dependency_overrides[get_current_user] = _override_user_a
        cleanup_permission_cache()

        response = await client.get("/api/v1/alumno/dashboard")
        assert response.status_code == 200
        body = response.json()

        # Tenant A user should see 0 materias (we didn't create any in Tenant A)
        assert len(body["materias"]) == 0, (
            "Tenant A user should not see Tenant B materias"
        )

        # Verify that 'Física I' does not appear in the response
        materia_nombres = [m["nombre"] for m in body["materias"]]
        assert "Física I" not in materia_nombres
