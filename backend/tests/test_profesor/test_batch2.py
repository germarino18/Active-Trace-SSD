"""Integration tests — batch 2 profesor endpoints (backend-batch2).

Items covered:
  - Item 5: GET /api/v1/profesor/atrasados (cross-materia)
  - Item 6: bulk add alumnos + bulk-baja + calificaciones persist after baja

TDD cycle per feature:
  Safety net: 67 tests passed before this file.
  RED → write test
  GREEN → implement
  TRIANGULATE → multiple cases
  REFACTOR → clean up
"""

import datetime
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.models.actividad import Actividad
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


# ── Helpers ───────────────────────────────────────────────────────────────────


async def _create_dictado_with_padron_and_actividad(
    db_session, tenant_id, user_id, materia_nombre="Matemática", n_alumnos=2
):
    """Create full structure: carrera/materia/cohorte/dictado/version/entradas/actividad."""
    c_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=tenant_id)
    carrera = await c_repo.create({"codigo": f"CR-{uuid.uuid4().hex[:4]}", "nombre": "Carrera"})
    m_repo = BaseRepository(model=Materia, session=db_session, tenant_id=tenant_id)
    materia = await m_repo.create({"codigo": f"MT-{uuid.uuid4().hex[:4]}", "nombre": materia_nombre})
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
    for i in range(n_alumnos):
        ep = await ep_repo.create(
            {
                "version_id": version.id,
                "nombre": f"Alumno{i}",
                "apellidos": "Test",
                "email": f"a{i}@test.com",
            }
        )
        entradas.append(ep)

    # Actividad with past fecha_limite
    act_repo = BaseRepository(model=Actividad, session=db_session, tenant_id=tenant_id)
    actividad = await act_repo.create(
        {
            "dictado_id": dictado.id,
            "nombre": "TP 1",
            "tipo": "TP",
            "fecha_limite": datetime.date(2025, 1, 1),
        }
    )

    return {
        "dictado": dictado,
        "materia": materia,
        "version": version,
        "entradas": entradas,
        "actividad": actividad,
        "usuario": usuario,
        "carrera": carrera,
        "cohorte": cohorte,
    }


async def _create_alumno_usuario(db_session, tenant_id):
    """Create a User + Usuario with ALUMNO role (for picker tests)."""
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=tenant_id)
    alumno_user = await user_repo.create(
        {
            "email": f"alumno-pick-{uuid.uuid4().hex[:6]}@test.com",
            "password_hash": "hash",
            "display_name": "Alumno",
            "is_active": True,
            "roles": ["ALUMNO"],
        }
    )
    u_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=tenant_id)
    alumno_usuario = await u_repo.create(
        {
            "user_id": alumno_user.id,
            "nombre": "Alice",
            "apellidos": "Test",
            "estado": "Activo",
            "facturador": False,
        }
    )
    asig_repo = BaseRepository(model=Asignacion, session=db_session, tenant_id=tenant_id)
    await asig_repo.create(
        {
            "usuario_id": alumno_usuario.id,
            "rol": "ALUMNO",
            "desde": datetime.date.today(),
            "hasta": None,
        }
    )
    return alumno_usuario


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
async def auth_user(db_session, test_tenant) -> CurrentUser:
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    user = await user_repo.create(
        {
            "email": f"prof-pb2-{uuid.uuid4().hex[:8]}@test.com",
            "password_hash": "hash",
            "display_name": "Prof B2",
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
            "email": f"alumno-pb2-{uuid.uuid4().hex[:8]}@test.com",
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


# ── Item 5: GET /profesor/atrasados (cross-materia) ──────────────────────────


class TestAtrasadosCrossMateria:
    """Item 5: GET /api/v1/profesor/atrasados — cross-materia atrasados.

    TDD: RED → GREEN → TRIANGULATE
    Safety net: 67 tests before this file.
    """

    async def test_retorna_alumnos_sin_entrega(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """GREEN: returns alumnos with ≥1 actividad sin entrega."""
        setup = await _create_dictado_with_padron_and_actividad(
            db_session, test_tenant.id, auth_user.user_id
        )
        # No calificaciones → all alumnos have sin_entrega for TP 1

        resp = await client.get("/api/v1/profesor/atrasados")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 2  # 2 alumnos in padrón, both sin entrega

        ids = [a["entrada_padron_id"] for a in data]
        for ep in setup["entradas"]:
            assert str(ep.id) in ids

        for a in data:
            assert "actividades_sin_entrega" in a
            assert "TP 1" in a["actividades_sin_entrega"]
            assert "materia_nombre" in a
            assert "dictado_id" in a

    async def test_excluye_alumnos_con_todas_las_entregas(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """TRIANGULATE: alumno con TP1 entregado no aparece en atrasados."""
        setup = await _create_dictado_with_padron_and_actividad(
            db_session, test_tenant.id, auth_user.user_id
        )
        actividad = setup["actividad"]
        entrada_con_entrega = setup["entradas"][0]
        entrada_sin_entrega = setup["entradas"][1]

        # First alumno has calificacion (entregado — even if desaprobado)
        calif_repo = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
        await calif_repo.upsert_for_actividad(
            entrada_padron_id=entrada_con_entrega.id,
            dictado_id=setup["dictado"].id,
            actividad_id=actividad.id,
            actividad_nombre=actividad.nombre,
            nota_numerica=4.0,
            nota_textual=None,
            aprobado=False,  # desaprobado but has a row → NOT sin_entrega
        )
        await db_session.commit()

        resp = await client.get("/api/v1/profesor/atrasados")
        assert resp.status_code == 200
        data = resp.json()

        ids = [a["entrada_padron_id"] for a in data]
        assert str(entrada_sin_entrega.id) in ids
        assert str(entrada_con_entrega.id) not in ids  # has row → not sin_entrega

    async def test_tenant_isolation(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, another_tenant, auth_user
    ):
        """TRIANGULATE: datos de otro tenant no aparecen."""
        # Create data in another_tenant — should not show up
        await _create_dictado_with_padron_and_actividad(
            db_session, another_tenant.id, auth_user.user_id
        )
        # Nothing in test_tenant → empty result
        resp = await client.get("/api/v1/profesor/atrasados")
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_sin_permiso_403(
        self, app, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user_alumno
    ):
        """TRIANGULATE: sin atrasados:ver → 403 (fail-closed)."""
        from tests.helpers import cleanup_permission_cache as _cleanup

        async def _override_no_perm():
            return auth_user_alumno

        app.dependency_overrides[get_current_user] = _override_no_perm
        _cleanup()
        try:
            resp = await client.get("/api/v1/profesor/atrasados")
            assert resp.status_code == 403
        finally:
            _cleanup()

    async def test_cross_materia_multiples_dictados(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """TRIANGULATE: retorna alumnos de múltiples materias del profesor."""
        s1 = await _create_dictado_with_padron_and_actividad(
            db_session, test_tenant.id, auth_user.user_id, materia_nombre="Física"
        )
        s2 = await _create_dictado_with_padron_and_actividad(
            db_session, test_tenant.id, auth_user.user_id, materia_nombre="Química"
        )

        resp = await client.get("/api/v1/profesor/atrasados")
        assert resp.status_code == 200
        data = resp.json()

        # Should contain alumnos from both materias (2 from each = 4 total)
        assert len(data) == 4
        materias = {a["materia_nombre"] for a in data}
        assert "Física" in materias
        assert "Química" in materias


# ── Item 6: Bulk add / baja masiva ───────────────────────────────────────────


class TestBulkAddAlumnos:
    """Item 6a: POST con usuario_ids (lista) — bulk alta.

    TDD: RED → GREEN → TRIANGULATE
    Safety net: 67 tests before this file.
    """

    async def test_bulk_add_agrega_todos(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """GREEN: bulk add enrolls all usuario_ids."""
        setup = await _create_dictado_with_padron_and_actividad(
            db_session, test_tenant.id, auth_user.user_id, n_alumnos=0
        )

        alumno1 = await _create_alumno_usuario(db_session, test_tenant.id)
        alumno2 = await _create_alumno_usuario(db_session, test_tenant.id)

        resp = await client.post(
            f"/api/v1/profesor/dictados/{setup['dictado'].id}/padron/alumnos",
            json={"usuario_ids": [str(alumno1.id), str(alumno2.id)]},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 2
        nombres = {e["nombre"] for e in data}
        assert "Alice" in nombres

    async def test_bulk_add_tenant_isolation(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, another_tenant, auth_user
    ):
        """TRIANGULATE: dictado de otro tenant → 404."""
        setup_otro = await _create_dictado_with_padron_and_actividad(
            db_session, another_tenant.id, auth_user.user_id, n_alumnos=0
        )
        alumno = await _create_alumno_usuario(db_session, test_tenant.id)

        resp = await client.post(
            f"/api/v1/profesor/dictados/{setup_otro['dictado'].id}/padron/alumnos",
            json={"usuario_ids": [str(alumno.id)]},
        )
        assert resp.status_code == 404

    async def test_single_add_still_works(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """TRIANGULATE: single usuario_id path still works (backward compat)."""
        setup = await _create_dictado_with_padron_and_actividad(
            db_session, test_tenant.id, auth_user.user_id, n_alumnos=0
        )
        alumno = await _create_alumno_usuario(db_session, test_tenant.id)

        resp = await client.post(
            f"/api/v1/profesor/dictados/{setup['dictado'].id}/padron/alumnos",
            json={"usuario_id": str(alumno.id)},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["nombre"] == "Alice"


class TestBulkBajaAlumnos:
    """Item 6b: POST /padron/alumnos/bulk-baja — baja masiva con califs persistentes.

    TDD: RED → GREEN → TRIANGULATE
    Safety net: 67 tests before this file.
    """

    async def test_bulk_baja_soft_deletes_all(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """GREEN: bulk baja soft-deletes all entries (deleted_at set)."""
        setup = await _create_dictado_with_padron_and_actividad(
            db_session, test_tenant.id, auth_user.user_id, n_alumnos=2
        )
        entradas = setup["entradas"]

        resp = await client.post(
            f"/api/v1/profesor/dictados/{setup['dictado'].id}/padron/alumnos/bulk-baja",
            json={"entrada_padron_ids": [str(e.id) for e in entradas]},
        )
        assert resp.status_code == 204

        # Verify soft deleted (deleted_at set)
        ep_repo = BaseRepository(model=EntradaPadron, session=db_session, tenant_id=test_tenant.id)
        ep_repo._include_soft_deleted = True
        for ep in entradas:
            reloaded = await ep_repo.find_by_id(ep.id)
            assert reloaded is not None
            assert reloaded.deleted_at is not None

    async def test_calificaciones_persisten_despues_de_baja(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """GREEN: after bulk baja, Calificacion rows STILL EXIST (no cascade)."""
        setup = await _create_dictado_with_padron_and_actividad(
            db_session, test_tenant.id, auth_user.user_id, n_alumnos=1
        )
        entrada = setup["entradas"][0]
        actividad = setup["actividad"]

        # Create calificacion BEFORE baja
        calif_repo = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
        await calif_repo.upsert_for_actividad(
            entrada_padron_id=entrada.id,
            dictado_id=setup["dictado"].id,
            actividad_id=actividad.id,
            actividad_nombre=actividad.nombre,
            nota_numerica=7.0,
            nota_textual=None,
            aprobado=True,
        )
        await db_session.commit()

        # Baja
        resp = await client.post(
            f"/api/v1/profesor/dictados/{setup['dictado'].id}/padron/alumnos/bulk-baja",
            json={"entrada_padron_ids": [str(entrada.id)]},
        )
        assert resp.status_code == 204

        # Calificaciones must still exist — query directly
        from sqlalchemy import select
        from app.models.calificacion import Calificacion

        q = select(Calificacion).where(
            Calificacion.tenant_id == test_tenant.id,
            Calificacion.entrada_padron_id == entrada.id,
        )
        r = await db_session.execute(q)
        califs = list(r.unique().scalars().all())
        assert len(califs) == 1
        assert float(califs[0].nota_numerica) == 7.0

    async def test_bulk_baja_tenant_isolation(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, another_tenant, auth_user
    ):
        """TRIANGULATE: bulk baja of entries from otro tenant → 404."""
        setup_otro = await _create_dictado_with_padron_and_actividad(
            db_session, another_tenant.id, auth_user.user_id, n_alumnos=1
        )
        entrada_otro = setup_otro["entradas"][0]

        # Even the dictado is from another tenant, we expect 404
        resp = await client.post(
            f"/api/v1/profesor/dictados/{setup_otro['dictado'].id}/padron/alumnos/bulk-baja",
            json={"entrada_padron_ids": [str(entrada_otro.id)]},
        )
        assert resp.status_code == 404

    async def test_bulk_baja_sin_permiso_403(
        self, app, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user_alumno
    ):
        """TRIANGULATE: sin padron:gestionar-alumno → 403 (fail-closed)."""
        from tests.helpers import cleanup_permission_cache as _cleanup

        async def _override_no_perm():
            return auth_user_alumno

        app.dependency_overrides[get_current_user] = _override_no_perm
        _cleanup()
        try:
            resp = await client.post(
                f"/api/v1/profesor/dictados/{uuid.uuid4()}/padron/alumnos/bulk-baja",
                json={"entrada_padron_ids": [str(uuid.uuid4())]},
            )
            assert resp.status_code == 403
        finally:
            _cleanup()

    async def test_campo_extra_bulk_baja_rechazado(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """TRIANGULATE: campo extra → 422 (extra='forbid')."""
        setup = await _create_dictado_with_padron_and_actividad(
            db_session, test_tenant.id, auth_user.user_id, n_alumnos=1
        )
        resp = await client.post(
            f"/api/v1/profesor/dictados/{setup['dictado'].id}/padron/alumnos/bulk-baja",
            json={
                "entrada_padron_ids": [str(setup["entradas"][0].id)],
                "campo_extra": "no",
            },
        )
        assert resp.status_code == 422
