"""Integration tests — batch 2 actividades endpoints (backend-batch2).

Items covered:
  - Item 2: plantilla-csv pre-filled with existing calificaciones
  - Item 3: POST /api/v1/actividades/{actividad_id}/calificaciones (modal individual)
  - Item 4: Classification logic (aprobado field, sin_entrega vs desaprobado)

TDD cycle per feature:
  Safety net: 67 tests passed before this file was written.
  RED → write test (endpoint/behaviour doesn't exist yet)
  GREEN → implement minimum
  TRIANGULATE → multiple cases
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


# ── Fixtures & helpers ────────────────────────────────────────────────────────


async def _create_full_setup(db_session, tenant_id, user_id, n_alumnos=3):
    """Create carrera/materia/cohorte/dictado/version/entradas + actividad."""
    c_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=tenant_id)
    carrera = await c_repo.create({"codigo": f"B2-{uuid.uuid4().hex[:4]}", "nombre": "B2"})
    m_repo = BaseRepository(model=Materia, session=db_session, tenant_id=tenant_id)
    materia = await m_repo.create({"codigo": f"B2M-{uuid.uuid4().hex[:4]}", "nombre": "Matemática 2024"})
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
                "email": f"alumno{i}@test.com",
            }
        )
        entradas.append(ep)

    # Create actividad (past fecha_limite = atrasado_null trigger)
    act_repo = BaseRepository(model=Actividad, session=db_session, tenant_id=tenant_id)
    actividad = await act_repo.create(
        {
            "dictado_id": dictado.id,
            "nombre": "TP 1",
            "tipo": "TP",
            "fecha_limite": datetime.date(2025, 1, 1),  # past
        }
    )

    return {
        "dictado": dictado,
        "materia": materia,
        "version": version,
        "entradas": entradas,
        "actividad": actividad,
        "usuario": usuario,
    }


@pytest.fixture
async def auth_user(db_session, test_tenant) -> CurrentUser:
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    user = await user_repo.create(
        {
            "email": f"prof-b2-{uuid.uuid4().hex[:8]}@test.com",
            "password_hash": "hash",
            "display_name": "Profesor B2",
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
            "email": f"alumno-b2-{uuid.uuid4().hex[:8]}@test.com",
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


# ── Item 2: plantilla-csv pre-filled ─────────────────────────────────────────


class TestPlantillaCSVPrefilled:
    """Item 2: plantilla-csv pre-fills nota/aprobado from existing calificaciones.

    TDD: RED → GREEN → TRIANGULATE → REFACTOR
    Safety net: 67 tests before this file.
    """

    async def test_plantilla_prefilled_con_calificacion_existente(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """GREEN: nota/aprobado pre-filled for alumnos WITH calificacion."""
        setup = await _create_full_setup(db_session, test_tenant.id, auth_user.user_id)
        actividad = setup["actividad"]
        entrada = setup["entradas"][0]

        # Create calificacion for first alumno
        calif_repo = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
        await calif_repo.upsert_for_actividad(
            entrada_padron_id=entrada.id,
            dictado_id=setup["dictado"].id,
            actividad_id=actividad.id,
            actividad_nombre=actividad.nombre,
            nota_numerica=8.5,
            nota_textual=None,
            aprobado=True,
        )
        await db_session.commit()

        resp = await client.get(f"/api/v1/actividades/{actividad.id}/plantilla-csv")
        assert resp.status_code == 200

        rows = list(csv.DictReader(io.StringIO(resp.text)))
        assert len(rows) == 3

        # First row (entrada[0]) should have nota=8.5 and aprobado=true
        row_0 = next(r for r in rows if r["entrada_padron_id"] == str(entrada.id))
        assert row_0["nota"] == "8.5"
        assert row_0["aprobado"] == "true"

    async def test_plantilla_prefilled_sin_calificacion_vacio(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """TRIANGULATE: alumnos WITHOUT calificacion get empty nota/aprobado."""
        setup = await _create_full_setup(db_session, test_tenant.id, auth_user.user_id)
        actividad = setup["actividad"]
        # Don't create any calificaciones

        resp = await client.get(f"/api/v1/actividades/{actividad.id}/plantilla-csv")
        assert resp.status_code == 200

        rows = list(csv.DictReader(io.StringIO(resp.text)))
        for row in rows:
            assert row["nota"] == ""
            assert row["aprobado"] == ""

    async def test_plantilla_prefilled_desaprobado(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """TRIANGULATE: desaprobado row shows nota and aprobado=false."""
        setup = await _create_full_setup(db_session, test_tenant.id, auth_user.user_id)
        actividad = setup["actividad"]
        entrada = setup["entradas"][1]

        calif_repo = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
        await calif_repo.upsert_for_actividad(
            entrada_padron_id=entrada.id,
            dictado_id=setup["dictado"].id,
            actividad_id=actividad.id,
            actividad_nombre=actividad.nombre,
            nota_numerica=3.0,
            nota_textual=None,
            aprobado=False,
        )
        await db_session.commit()

        resp = await client.get(f"/api/v1/actividades/{actividad.id}/plantilla-csv")
        rows = list(csv.DictReader(io.StringIO(resp.text)))
        row_1 = next(r for r in rows if r["entrada_padron_id"] == str(entrada.id))
        assert row_1["nota"] == "3.0"
        assert row_1["aprobado"] == "false"

    async def test_plantilla_prefilled_mix_states(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """TRIANGULATE: mix — some with nota, some empty; all correct."""
        setup = await _create_full_setup(db_session, test_tenant.id, auth_user.user_id)
        actividad = setup["actividad"]
        entradas = setup["entradas"]

        calif_repo = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
        # Only first alumno has calificacion
        await calif_repo.upsert_for_actividad(
            entrada_padron_id=entradas[0].id,
            dictado_id=setup["dictado"].id,
            actividad_id=actividad.id,
            actividad_nombre=actividad.nombre,
            nota_numerica=9.0,
            nota_textual=None,
            aprobado=True,
        )
        await db_session.commit()

        resp = await client.get(f"/api/v1/actividades/{actividad.id}/plantilla-csv")
        rows = {r["entrada_padron_id"]: r for r in csv.DictReader(io.StringIO(resp.text))}

        assert rows[str(entradas[0].id)]["nota"] == "9.0"
        assert rows[str(entradas[0].id)]["aprobado"] == "true"
        assert rows[str(entradas[1].id)]["nota"] == ""
        assert rows[str(entradas[2].id)]["nota"] == ""


# ── Item 3: POST /calificaciones (modal individual) ────────────────────────────


class TestRegistrarCalificacionIndividual:
    """Item 3: POST /api/v1/actividades/{id}/calificaciones — modal upsert.

    TDD: RED → GREEN → TRIANGULATE
    Safety net: 67 tests before this file.
    """

    async def test_crear_calificacion_individual_201(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """GREEN: nueva calificacion retorna 201 con datos correctos."""
        setup = await _create_full_setup(db_session, test_tenant.id, auth_user.user_id)
        actividad = setup["actividad"]
        entrada = setup["entradas"][0]

        resp = await client.post(
            f"/api/v1/actividades/{actividad.id}/calificaciones",
            json={
                "entrada_padron_id": str(entrada.id),
                "nota_numerica": 8.0,
                "aprobado": True,
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["aprobado"] is True
        assert float(data["nota_numerica"]) == 8.0
        assert data["origen"] == "Manual"
        assert data["actividad"] == "TP 1"
        assert data["actividad_id"] == str(actividad.id)

    async def test_upsert_no_duplica(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """TRIANGULATE: segunda llamada actualiza, no duplica."""
        setup = await _create_full_setup(db_session, test_tenant.id, auth_user.user_id)
        actividad = setup["actividad"]
        entrada = setup["entradas"][0]

        # First call
        await client.post(
            f"/api/v1/actividades/{actividad.id}/calificaciones",
            json={"entrada_padron_id": str(entrada.id), "nota_numerica": 5.0, "aprobado": False},
        )

        # Second call — update
        resp2 = await client.post(
            f"/api/v1/actividades/{actividad.id}/calificaciones",
            json={"entrada_padron_id": str(entrada.id), "nota_numerica": 9.0, "aprobado": True},
        )
        assert resp2.status_code == 201

        # Verify only ONE row in DB
        calif_repo = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
        califs = await calif_repo.find_by_dictado(setup["dictado"].id)
        linked = [c for c in califs if c.actividad_id == actividad.id]
        assert len(linked) == 1
        assert float(linked[0].nota_numerica) == 9.0
        assert linked[0].aprobado is True

    async def test_entrada_no_pertenece_al_dictado_422(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """TRIANGULATE: entrada_padron de otro dictado → 422."""
        setup = await _create_full_setup(db_session, test_tenant.id, auth_user.user_id)
        actividad = setup["actividad"]

        # Create a SEPARATE materia/carrera/cohorte so unique constraint doesn't fire
        c_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=test_tenant.id)
        carrera2 = await c_repo.create({"codigo": f"OT2-{uuid.uuid4().hex[:4]}", "nombre": "Otra2"})
        m_repo = BaseRepository(model=Materia, session=db_session, tenant_id=test_tenant.id)
        materia2 = await m_repo.create({"codigo": f"OM2-{uuid.uuid4().hex[:4]}", "nombre": "OtraM2"})
        co_repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=test_tenant.id)
        cohorte2 = await co_repo.create({"carrera_id": carrera2.id, "nombre": "2025", "anio": 2025})
        d_repo = DictadoRepository(session=db_session, tenant_id=test_tenant.id)
        dictado2 = await d_repo.create(
            {"materia_id": materia2.id, "carrera_id": carrera2.id, "cohorte_id": cohorte2.id}
        )
        vp_repo = BaseRepository(model=VersionPadron, session=db_session, tenant_id=test_tenant.id)
        version2 = await vp_repo.create(
            {"dictado_id": dictado2.id, "cargado_por": setup["usuario"].id, "activa": True}
        )
        ep_repo = BaseRepository(model=EntradaPadron, session=db_session, tenant_id=test_tenant.id)
        entrada_otro = await ep_repo.create(
            {"version_id": version2.id, "nombre": "Otro", "apellidos": "Dictado"}
        )

        resp = await client.post(
            f"/api/v1/actividades/{actividad.id}/calificaciones",
            json={"entrada_padron_id": str(entrada_otro.id), "aprobado": True},
        )
        assert resp.status_code == 422

    async def test_otro_tenant_404(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, another_tenant, auth_user
    ):
        """TRIANGULATE: actividad de otro tenant → 404."""
        setup_otro = await _create_full_setup(db_session, another_tenant.id, auth_user.user_id)
        actividad_otro = setup_otro["actividad"]
        entrada_otro = setup_otro["entradas"][0]

        resp = await client.post(
            f"/api/v1/actividades/{actividad_otro.id}/calificaciones",
            json={"entrada_padron_id": str(entrada_otro.id), "aprobado": True},
        )
        assert resp.status_code == 404

    async def test_sin_permiso_403(
        self, app, client: AsyncClient, db_session: AsyncSession, test_tenant,
        auth_user_alumno
    ):
        """TRIANGULATE: sin calificaciones:editar → 403 (fail-closed)."""
        from tests.helpers import cleanup_permission_cache as _cleanup

        async def _override_no_perm():
            return auth_user_alumno

        app.dependency_overrides[get_current_user] = _override_no_perm
        _cleanup()
        try:
            resp = await client.post(
                f"/api/v1/actividades/{uuid.uuid4()}/calificaciones",
                json={"entrada_padron_id": str(uuid.uuid4()), "aprobado": True},
            )
            assert resp.status_code == 403
        finally:
            _cleanup()

    async def test_campo_extra_rechazado_422(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """TRIANGULATE: campo extra en body → 422 (extra='forbid')."""
        setup = await _create_full_setup(db_session, test_tenant.id, auth_user.user_id)
        actividad = setup["actividad"]
        entrada = setup["entradas"][0]

        resp = await client.post(
            f"/api/v1/actividades/{actividad.id}/calificaciones",
            json={
                "entrada_padron_id": str(entrada.id),
                "aprobado": True,
                "campo_no_declarado": "valor",
            },
        )
        assert resp.status_code == 422

    async def test_aprobado_false_desaprobado(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """TRIANGULATE: aprobado=False se guarda correctamente como desaprobado."""
        setup = await _create_full_setup(db_session, test_tenant.id, auth_user.user_id)
        actividad = setup["actividad"]
        entrada = setup["entradas"][2]

        resp = await client.post(
            f"/api/v1/actividades/{actividad.id}/calificaciones",
            json={"entrada_padron_id": str(entrada.id), "nota_numerica": 2.5, "aprobado": False},
        )
        assert resp.status_code == 201
        assert resp.json()["aprobado"] is False


# ── Item 4: Classification review ────────────────────────────────────────────


class TestClasificacionAlumnos:
    """Item 4: Classification logic using aprobado field directly.

    Rules:
    - no calificacion + actividad vencida → sin_entrega (atrasado_null)
    - calificacion.aprobado=True → OK
    - calificacion.aprobado=False → desaprobado
    - alumno con TP1 aprobado + TP2 sin entrega → atrasado (sin entrega de TP2)
    - alumno con ambos aprobados → aprobado
    - alumno con un desaprobado → atrasado (desaprobado)

    TDD: RED → GREEN → TRIANGULATE
    Safety net: 67 tests before this file.
    """

    async def _setup_dos_actividades(self, db_session, tenant_id, user_id):
        """Setup with TWO actividades, both with past fecha_limite."""
        setup = await _create_full_setup(db_session, tenant_id, user_id, n_alumnos=3)

        act_repo = BaseRepository(model=Actividad, session=db_session, tenant_id=tenant_id)
        actividad2 = await act_repo.create(
            {
                "dictado_id": setup["dictado"].id,
                "nombre": "TP 2",
                "tipo": "TP",
                "fecha_limite": datetime.date(2025, 2, 1),  # past
            }
        )
        return setup, actividad2

    async def test_alumno_tp1_aprobado_tp2_sin_entrega_es_atrasado(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """GREEN: TP1 aprobado + TP2 sin entrega → atrasado (sin entrega TP2)."""
        setup, actividad2 = await self._setup_dos_actividades(
            db_session, test_tenant.id, auth_user.user_id
        )
        actividad1 = setup["actividad"]
        entrada = setup["entradas"][0]

        # TP1 approved
        calif_repo = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
        await calif_repo.upsert_for_actividad(
            entrada_padron_id=entrada.id,
            dictado_id=setup["dictado"].id,
            actividad_id=actividad1.id,
            actividad_nombre=actividad1.nombre,
            nota_numerica=8.0,
            nota_textual=None,
            aprobado=True,
        )
        # No calificacion for TP2
        await db_session.commit()

        resp = await client.get(
            f"/api/v1/profesor/dictados/{setup['dictado'].id}/atrasados"
        )
        assert resp.status_code == 200
        data = resp.json()

        alumno = next(a for a in data if a["alumno_id"] == str(entrada.id))
        assert alumno["estado"] == "atrasado"
        assert alumno["subtipo"] == "atrasado_null"
        assert "TP 2" in alumno["actividades_atrasado_null"]
        assert "TP 2" not in alumno["actividades_desaprobadas"]

    async def test_alumno_con_ambos_aprobados_es_aprobado(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """TRIANGULATE: ambos TPs aprobados → estado=aprobado."""
        setup, actividad2 = await self._setup_dos_actividades(
            db_session, test_tenant.id, auth_user.user_id
        )
        actividad1 = setup["actividad"]
        entrada = setup["entradas"][0]

        calif_repo = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
        for act in [actividad1, actividad2]:
            await calif_repo.upsert_for_actividad(
                entrada_padron_id=entrada.id,
                dictado_id=setup["dictado"].id,
                actividad_id=act.id,
                actividad_nombre=act.nombre,
                nota_numerica=8.0,
                nota_textual=None,
                aprobado=True,
            )
        await db_session.commit()

        resp = await client.get(
            f"/api/v1/profesor/dictados/{setup['dictado'].id}/atrasados"
        )
        assert resp.status_code == 200
        data = resp.json()

        alumno = next(a for a in data if a["alumno_id"] == str(entrada.id))
        assert alumno["estado"] == "aprobado"

    async def test_alumno_con_desaprobado_es_atrasado_desaprobado(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """TRIANGULATE: calificacion con aprobado=False → atrasado (desaprobado)."""
        setup = await _create_full_setup(db_session, test_tenant.id, auth_user.user_id)
        actividad = setup["actividad"]
        entrada = setup["entradas"][0]

        calif_repo = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
        await calif_repo.upsert_for_actividad(
            entrada_padron_id=entrada.id,
            dictado_id=setup["dictado"].id,
            actividad_id=actividad.id,
            actividad_nombre=actividad.nombre,
            nota_numerica=3.0,
            nota_textual=None,
            aprobado=False,
        )
        await db_session.commit()

        resp = await client.get(
            f"/api/v1/profesor/dictados/{setup['dictado'].id}/atrasados"
        )
        assert resp.status_code == 200
        data = resp.json()

        alumno = next(a for a in data if a["alumno_id"] == str(entrada.id))
        assert alumno["estado"] == "atrasado"
        assert alumno["subtipo"] == "desaprobado"
        assert actividad.nombre in alumno["actividades_desaprobadas"]

    async def test_alumno_sin_entrega_actividad_sin_fecha_limite_no_atrasado(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """TRIANGULATE: ONLY actividad sin fecha_limite — sin entrega no es atrasado_null.

        Creates a fresh dictado WITHOUT a vencida actividad, only one without fecha_limite.
        """
        # Create a separate dictado with ONLY a sin-fecha-limite actividad
        c_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=test_tenant.id)
        carrera = await c_repo.create({"codigo": f"SFL-{uuid.uuid4().hex[:4]}", "nombre": "SFL"})
        m_repo = BaseRepository(model=Materia, session=db_session, tenant_id=test_tenant.id)
        materia = await m_repo.create({"codigo": f"SFLM-{uuid.uuid4().hex[:4]}", "nombre": "SFLMat"})
        co_repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=test_tenant.id)
        cohorte = await co_repo.create({"carrera_id": carrera.id, "nombre": "2025", "anio": 2025})
        d_repo = DictadoRepository(session=db_session, tenant_id=test_tenant.id)
        dictado = await d_repo.create(
            {"materia_id": materia.id, "carrera_id": carrera.id, "cohorte_id": cohorte.id}
        )

        u_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
        existing = await u_repo.find_by(user_id=auth_user.user_id)
        usuario = existing[0] if existing else await u_repo.create(
            {"user_id": auth_user.user_id, "nombre": "Profe", "apellidos": "Test", "estado": "Activo", "facturador": False}
        )

        vp_repo = BaseRepository(model=VersionPadron, session=db_session, tenant_id=test_tenant.id)
        version = await vp_repo.create(
            {"dictado_id": dictado.id, "cargado_por": usuario.id, "activa": True}
        )
        ep_repo = BaseRepository(model=EntradaPadron, session=db_session, tenant_id=test_tenant.id)
        entrada = await ep_repo.create(
            {"version_id": version.id, "nombre": "Alumno", "apellidos": "Test"}
        )

        # Create actividad WITHOUT fecha_limite
        act_repo = BaseRepository(model=Actividad, session=db_session, tenant_id=test_tenant.id)
        await act_repo.create(
            {
                "dictado_id": dictado.id,
                "nombre": "Parcial Optativo",
                "tipo": "Parcial",
                "fecha_limite": None,  # no fecha_limite → sin entrega is NOT atrasado_null
            }
        )
        await db_session.commit()
        # No calificaciones

        resp = await client.get(
            f"/api/v1/profesor/dictados/{dictado.id}/atrasados"
        )
        assert resp.status_code == 200
        for alumno in resp.json():
            assert alumno["subtipo"] != "atrasado_null"
            assert alumno["estado"] == "aprobado"
