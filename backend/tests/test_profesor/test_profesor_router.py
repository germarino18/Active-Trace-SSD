"""Integration tests for profesor router (C-25 §4, §5, §6, §7, §8, §9).

TDD: RED → GREEN → TRIANGULATE → REFACTOR.
"""

import datetime
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


# ── Shared test helpers ────────────────────────────────────────────────────────


async def _create_full_dictado(
    db_session: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID
) -> dict:
    """Create carrera/materia/cohorte/dictado/usuario/asignacion/version/entradas."""
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
    asignacion = await asig_repo.create(
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
    for i in range(2):
        ep = await ep_repo.create(
            {
                "version_id": version.id,
                "nombre": f"Alumno{i}",
                "apellidos": "Test",
                "email": f"alumno{i}@test.com",
            }
        )
        entradas.append(ep)

    return {
        "carrera": carrera,
        "materia": materia,
        "cohorte": cohorte,
        "dictado": dictado,
        "usuario": usuario,
        "asignacion": asignacion,
        "version": version,
        "entradas": entradas,
    }


@pytest.fixture
async def auth_user(db_session, test_tenant) -> CurrentUser:
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    user = await user_repo.create(
        {
            "email": f"prof-{uuid.uuid4().hex[:8]}@test.com",
            "password_hash": "hash",
            "display_name": "Prof",
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


# ── §4 Dashboard ───────────────────────────────────────────────────────────────


class TestDashboard:
    async def test_dashboard_sin_dictados_retorna_vacios(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """GREEN: profesor sin dictados devuelve dashboard vacío."""
        resp = await client.get("/api/v1/profesor/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        assert data["materias_asignadas"] == []
        assert data["total_alumnos"] == 0

    async def test_dashboard_con_dictado_incluye_materia(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """TRIANGULATE: dashboard con dictado incluye la materia asignada."""
        await _create_full_dictado(db_session, test_tenant.id, auth_user.user_id)

        resp = await client.get("/api/v1/profesor/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["materias_asignadas"]) == 1
        assert data["total_alumnos"] == 2  # 2 entradas creadas

    async def test_dashboard_asignacion_vencida_excluida(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """TRIANGULATE: asignación vencida no aparece en dashboard."""
        # Create dictado with EXPIRED asignacion
        c_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=test_tenant.id)
        carrera = await c_repo.create({"codigo": f"VV-{uuid.uuid4().hex[:4]}", "nombre": "Vencida"})
        m_repo = BaseRepository(model=Materia, session=db_session, tenant_id=test_tenant.id)
        materia = await m_repo.create({"codigo": f"VVM-{uuid.uuid4().hex[:4]}", "nombre": "VVMateria"})
        co_repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=test_tenant.id)
        cohorte = await co_repo.create(
            {"carrera_id": carrera.id, "nombre": "2020", "anio": 2020}
        )
        d_repo = DictadoRepository(session=db_session, tenant_id=test_tenant.id)
        dictado = await d_repo.create(
            {"materia_id": materia.id, "carrera_id": carrera.id, "cohorte_id": cohorte.id}
        )

        u_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
        existing = await u_repo.find_by(user_id=auth_user.user_id)
        usuario = existing[0] if existing else await u_repo.create(
            {"user_id": auth_user.user_id, "nombre": "P", "apellidos": "T", "estado": "Activo", "facturador": False}
        )

        asig_repo = BaseRepository(model=Asignacion, session=db_session, tenant_id=test_tenant.id)
        await asig_repo.create(
            {
                "usuario_id": usuario.id,
                "rol": "PROFESOR",
                "dictado_id": dictado.id,
                "desde": datetime.date(2020, 1, 1),
                "hasta": datetime.date(2020, 12, 31),  # VENCIDA
            }
        )

        resp = await client.get("/api/v1/profesor/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        # No vencida asignacion should appear
        dictados_ids = [str(m["dictado_id"]) for m in data["materias_asignadas"]]
        assert str(dictado.id) not in dictados_ids


class TestMetricasDictado:
    async def test_metricas_dictado_sin_calificaciones_retorna_sin_datos(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """GREEN: dictado sin calificaciones devuelve sin_datos=True."""
        d = await _create_full_dictado(db_session, test_tenant.id, auth_user.user_id)

        resp = await client.get(
            f"/api/v1/profesor/dictados/{d['dictado'].id}/metricas"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["sin_datos"] is True

    async def test_metricas_otro_tenant_retorna_404(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, another_tenant, auth_user
    ):
        """TRIANGULATE: dictado de otro tenant → 404."""
        d = await _create_full_dictado(db_session, another_tenant.id, auth_user.user_id)

        resp = await client.get(
            f"/api/v1/profesor/dictados/{d['dictado'].id}/metricas"
        )
        assert resp.status_code == 404

    async def test_metricas_incluye_materia_nombre_y_cohorte_nombre(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """RED/GREEN: métricas devuelven materia_nombre y cohorte_nombre."""
        d = await _create_full_dictado(db_session, test_tenant.id, auth_user.user_id)

        resp = await client.get(
            f"/api/v1/profesor/dictados/{d['dictado'].id}/metricas"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["materia_nombre"] == "Matemática"
        assert data["cohorte_nombre"] == "2024"

    async def test_metricas_materia_nombre_segundo_dictado(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """TRIANGULATE: segundo dictado con distinta materia/cohorte."""
        # Create a second dictado with different materia and cohorte
        from app.models.carrera import Carrera
        from app.repositories.base import BaseRepository
        from app.repositories.dictado_repository import DictadoRepository

        c_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=test_tenant.id)
        carrera = await c_repo.create({"codigo": f"CS-{uuid.uuid4().hex[:4]}", "nombre": "Ciencias"})
        m_repo = BaseRepository(model=Materia, session=db_session, tenant_id=test_tenant.id)
        materia = await m_repo.create({"codigo": f"FIS-{uuid.uuid4().hex[:4]}", "nombre": "Física"})
        co_repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=test_tenant.id)
        cohorte = await co_repo.create({"carrera_id": carrera.id, "nombre": "2025", "anio": 2025})
        d_repo = DictadoRepository(session=db_session, tenant_id=test_tenant.id)
        dictado = await d_repo.create(
            {"materia_id": materia.id, "carrera_id": carrera.id, "cohorte_id": cohorte.id}
        )

        resp = await client.get(
            f"/api/v1/profesor/dictados/{dictado.id}/metricas"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["materia_nombre"] == "Física"
        assert data["cohorte_nombre"] == "2025"


# ── §5 Editar calificación ────────────────────────────────────────────────────


class TestEditarCalificacion:
    async def test_editar_nota_aprobado(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """GREEN: PATCH /calificaciones/{id} actualiza nota y aprobado."""
        d = await _create_full_dictado(db_session, test_tenant.id, auth_user.user_id)
        entrada = d["entradas"][0]

        # Create calificacion
        calif_repo = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
        calificacion = await calif_repo.create(
            {
                "entrada_padron_id": entrada.id,
                "dictado_id": d["dictado"].id,
                "actividad": "TP1",
                "nota_numerica": 4.0,
                "aprobado": False,
                "origen": "Manual",
            }
        )

        resp = await client.patch(
            f"/api/admin/calificaciones/{calificacion.id}",
            json={"nota_numerica": 8.5, "aprobado": True},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert float(data["nota_numerica"]) == 8.5
        assert data["aprobado"] is True

    async def test_editar_calificacion_sin_permiso_403(
        self, app, client: AsyncClient, db_session: AsyncSession, test_tenant,
        auth_user_no_perm
    ):
        """TRIANGULATE: usuario sin calificaciones:editar → 403."""
        from tests.helpers import cleanup_permission_cache as _cleanup

        async def _override_no_perm():
            return auth_user_no_perm

        app.dependency_overrides[get_current_user] = _override_no_perm
        _cleanup()
        try:
            fake_id = uuid.uuid4()
            resp = await client.patch(
                f"/api/admin/calificaciones/{fake_id}",
                json={"aprobado": True},
            )
            assert resp.status_code == 403
        finally:
            _cleanup()

    async def test_editar_calificacion_otro_tenant_404(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, another_tenant, auth_user
    ):
        """TRIANGULATE: calificacion de otro tenant → 404."""
        d = await _create_full_dictado(db_session, another_tenant.id, auth_user.user_id)
        entrada = d["entradas"][0]

        calif_repo = CalificacionRepository(session=db_session, tenant_id=another_tenant.id)
        calificacion = await calif_repo.create(
            {
                "entrada_padron_id": entrada.id,
                "dictado_id": d["dictado"].id,
                "actividad": "TP1",
                "nota_numerica": 5.0,
                "aprobado": False,
                "origen": "Manual",
            }
        )

        resp = await client.patch(
            f"/api/admin/calificaciones/{calificacion.id}",
            json={"nota_numerica": 9.0},
        )
        assert resp.status_code == 404

    async def test_editar_calificacion_campo_no_declarado_422(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """TRIANGULATE: campo extra en body → 422 (extra='forbid')."""
        fake_id = uuid.uuid4()
        resp = await client.patch(
            f"/api/admin/calificaciones/{fake_id}",
            json={"nota_numerica": 8.0, "campo_extra": "xxx"},
        )
        assert resp.status_code == 422


# ── §6 Gestión padrón ─────────────────────────────────────────────────────────


class TestPadronGestion:
    async def test_alta_alumno_returns_201(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """GREEN: POST alta de alumno devuelve 201."""
        d = await _create_full_dictado(db_session, test_tenant.id, auth_user.user_id)

        resp = await client.post(
            f"/api/v1/profesor/dictados/{d['dictado'].id}/padron/alumnos",
            json={"nombre": "Nuevo", "apellidos": "Alumno", "email": "nuevo@test.com"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["nombre"] == "Nuevo"
        assert data["apellidos"] == "Alumno"

    async def test_baja_alumno_soft_delete(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """GREEN: DELETE hace soft-delete; entrada permanece en DB con deleted_at."""
        d = await _create_full_dictado(db_session, test_tenant.id, auth_user.user_id)
        entrada = d["entradas"][0]

        resp = await client.delete(
            f"/api/v1/profesor/dictados/{d['dictado'].id}/padron/alumnos/{entrada.id}"
        )
        assert resp.status_code == 204

        # Verify soft deleted (not hard deleted)
        ep_repo = BaseRepository(model=EntradaPadron, session=db_session, tenant_id=test_tenant.id)
        ep_repo._include_soft_deleted = True
        reloaded = await ep_repo.find_by_id(entrada.id)
        assert reloaded is not None
        assert reloaded.deleted_at is not None

    async def test_baja_alumno_sin_permiso_403(
        self, app, client: AsyncClient, db_session: AsyncSession, test_tenant,
        auth_user_no_perm
    ):
        """TRIANGULATE: sin padron:gestionar-alumno → 403."""
        from tests.helpers import cleanup_permission_cache as _cleanup

        async def _override_no_perm():
            return auth_user_no_perm

        app.dependency_overrides[get_current_user] = _override_no_perm
        _cleanup()
        try:
            fake_dictado = uuid.uuid4()
            fake_entrada = uuid.uuid4()
            resp = await client.delete(
                f"/api/v1/profesor/dictados/{fake_dictado}/padron/alumnos/{fake_entrada}"
            )
            assert resp.status_code == 403
        finally:
            _cleanup()

    async def test_export_csv_retorna_csv(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """GREEN: GET export-csv devuelve content-type text/csv con alumnos."""
        d = await _create_full_dictado(db_session, test_tenant.id, auth_user.user_id)

        resp = await client.get(
            f"/api/v1/profesor/dictados/{d['dictado'].id}/padron/export-csv"
        )
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]
        body = resp.text
        assert "alumno_id" in body
        assert "Alumno0" in body

    async def test_tenant_isolation_baja_otro_tenant(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, another_tenant, auth_user
    ):
        """TRIANGULATE: baja alumno de otro tenant → 404."""
        d = await _create_full_dictado(db_session, another_tenant.id, auth_user.user_id)
        entrada = d["entradas"][0]

        resp = await client.delete(
            f"/api/v1/profesor/dictados/{d['dictado'].id}/padron/alumnos/{entrada.id}"
        )
        # The dictado won't be found in the current tenant scope → 404
        assert resp.status_code == 404


# ── §7 Atrasados clasificados ─────────────────────────────────────────────────


class TestAtrasadosClasificados:
    async def test_alumno_sin_calificaciones_es_aprobado(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """GREEN: alumno sin calificaciones NI actividades vencidas es aprobado."""
        d = await _create_full_dictado(db_session, test_tenant.id, auth_user.user_id)

        resp = await client.get(
            f"/api/v1/profesor/dictados/{d['dictado'].id}/atrasados"
        )
        assert resp.status_code == 200
        data = resp.json()
        # All alumnos are "aprobado" since no actividades with fecha_limite and no desaprobadas
        for alumno in data:
            assert alumno["estado"] == "aprobado"

    async def test_faltante_sin_fecha_limite_no_es_atrasado_null(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """TRIANGULATE: faltante SIN fecha_limite no es atrasado_null."""
        from app.schemas.actividades import ActividadCreate
        from app.services.actividad_service import ActividadService

        d = await _create_full_dictado(db_session, test_tenant.id, auth_user.user_id)

        # Create actividad WITHOUT fecha_limite
        svc = ActividadService.create(db_session, test_tenant.id)
        await svc.crear(
            d["dictado"].id,
            ActividadCreate(nombre="TP_sin_fecha", tipo="TP", fecha_limite=None),
        )

        # No calificaciones — but no fecha_limite means NOT atrasado_null
        resp = await client.get(
            f"/api/v1/profesor/dictados/{d['dictado'].id}/atrasados"
        )
        assert resp.status_code == 200
        for alumno in resp.json():
            assert alumno["subtipo"] != "atrasado_null"

    async def test_faltante_con_fecha_limite_vencida_es_atrasado_null(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """TRIANGULATE: faltante CON fecha_limite vencida SÍ es atrasado_null."""
        from app.schemas.actividades import ActividadCreate
        from app.services.actividad_service import ActividadService

        d = await _create_full_dictado(db_session, test_tenant.id, auth_user.user_id)

        # Create actividad WITH past fecha_limite
        svc = ActividadService.create(db_session, test_tenant.id)
        await svc.crear(
            d["dictado"].id,
            ActividadCreate(
                nombre="TP_vencido",
                tipo="TP",
                fecha_limite=datetime.date(2020, 1, 1),  # in the past
            ),
        )

        # No calificaciones → todos faltantes con fecha_limite vencida → atrasado_null
        resp = await client.get(
            f"/api/v1/profesor/dictados/{d['dictado'].id}/atrasados"
        )
        assert resp.status_code == 200
        for alumno in resp.json():
            assert alumno["estado"] == "atrasado"
            assert alumno["subtipo"] == "atrasado_null"

    async def test_tenant_isolation_otro_tenant_404(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, another_tenant, auth_user
    ):
        """TRIANGULATE: dictado de otro tenant → 404."""
        d = await _create_full_dictado(db_session, another_tenant.id, auth_user.user_id)

        resp = await client.get(
            f"/api/v1/profesor/dictados/{d['dictado'].id}/atrasados"
        )
        assert resp.status_code == 404


# ── §9 Equipo docente ─────────────────────────────────────────────────────────


class TestEquipoDocente:
    async def test_equipo_excluye_self(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """GREEN: equipo excluye al usuario actual."""
        d = await _create_full_dictado(db_session, test_tenant.id, auth_user.user_id)

        resp = await client.get(
            f"/api/v1/profesor/dictados/{d['dictado'].id}/equipo"
        )
        assert resp.status_code == 200
        data = resp.json()
        # No team members other than self (only the profesor was added)
        assert len(data) == 0

    async def test_equipo_incluye_companeros(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """TRIANGULATE: equipo incluye TUTOR del mismo dictado."""
        d = await _create_full_dictado(db_session, test_tenant.id, auth_user.user_id)

        # Add a TUTOR to the same dictado
        user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
        tutor_user = await user_repo.create(
            {
                "email": f"tutor-{uuid.uuid4().hex[:6]}@test.com",
                "password_hash": "hash",
                "display_name": "Tutor",
                "is_active": True,
                "roles": ["TUTOR"],
            }
        )
        u_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
        tutor_usuario = await u_repo.create(
            {"user_id": tutor_user.id, "nombre": "El", "apellidos": "Tutor", "estado": "Activo", "facturador": False}
        )
        asig_repo = BaseRepository(model=Asignacion, session=db_session, tenant_id=test_tenant.id)
        await asig_repo.create(
            {
                "usuario_id": tutor_usuario.id,
                "rol": "TUTOR",
                "dictado_id": d["dictado"].id,
                "desde": datetime.date.today(),
                "hasta": None,
            }
        )

        resp = await client.get(
            f"/api/v1/profesor/dictados/{d['dictado'].id}/equipo"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["rol"] == "TUTOR"
        assert data[0]["apellidos"] == "Tutor"

    async def test_equipo_dictado_sin_asignacion_404(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """TRIANGULATE: equipo de dictado donde profesor no tiene asignación → 404."""
        # Create a dictado without assigning auth_user
        c_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=test_tenant.id)
        carrera = await c_repo.create({"codigo": f"EQ-{uuid.uuid4().hex[:4]}", "nombre": "Eq"})
        m_repo = BaseRepository(model=Materia, session=db_session, tenant_id=test_tenant.id)
        materia = await m_repo.create({"codigo": f"EQM-{uuid.uuid4().hex[:4]}", "nombre": "EqMat"})
        co_repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=test_tenant.id)
        cohorte = await co_repo.create({"carrera_id": carrera.id, "nombre": "2024", "anio": 2024})
        d_repo = DictadoRepository(session=db_session, tenant_id=test_tenant.id)
        otro_dictado = await d_repo.create(
            {"materia_id": materia.id, "carrera_id": carrera.id, "cohorte_id": cohorte.id}
        )

        resp = await client.get(
            f"/api/v1/profesor/dictados/{otro_dictado.id}/equipo"
        )
        assert resp.status_code == 404

    async def test_equipo_excluye_asignacion_vencida(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """TRIANGULATE: miembro con asignacion vencida no aparece en equipo."""
        d = await _create_full_dictado(db_session, test_tenant.id, auth_user.user_id)

        # Add a TUTOR with EXPIRED asignacion
        user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
        tutor_user = await user_repo.create(
            {
                "email": f"tutor-exp-{uuid.uuid4().hex[:6]}@test.com",
                "password_hash": "hash",
                "display_name": "Expired",
                "is_active": True,
                "roles": ["TUTOR"],
            }
        )
        u_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
        tutor_usuario = await u_repo.create(
            {"user_id": tutor_user.id, "nombre": "Ex", "apellidos": "Tutor", "estado": "Activo", "facturador": False}
        )
        asig_repo = BaseRepository(model=Asignacion, session=db_session, tenant_id=test_tenant.id)
        await asig_repo.create(
            {
                "usuario_id": tutor_usuario.id,
                "rol": "TUTOR",
                "dictado_id": d["dictado"].id,
                "desde": datetime.date(2020, 1, 1),
                "hasta": datetime.date(2020, 12, 31),  # VENCIDA
            }
        )

        resp = await client.get(
            f"/api/v1/profesor/dictados/{d['dictado'].id}/equipo"
        )
        assert resp.status_code == 200
        data = resp.json()
        # Expired member should not appear
        assert all(m["apellidos"] != "Tutor" for m in data)


# ── NEW: §6 GET /padron + /alumnos-disponibles + alta con usuario_id ──────────


class TestGetPadron:
    """Integration tests for GET /api/v1/profesor/dictados/{id}/padron.

    TDD: RED → GREEN → TRIANGULATE.
    Safety net: existing 37 tests pass before this class was added.
    """

    async def test_get_padron_returns_entradas(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """GREEN: endpoint devuelve la lista de entradas del padrón activo."""
        d = await _create_full_dictado(db_session, test_tenant.id, auth_user.user_id)

        resp = await client.get(
            f"/api/v1/profesor/dictados/{d['dictado'].id}/padron"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 2  # 2 entradas creadas en _create_full_dictado
        assert data[0]["nombre"] == "Alumno0"

    async def test_get_padron_dictado_inexistente_404(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """TRIANGULATE: dictado que no existe → 404."""
        resp = await client.get(
            f"/api/v1/profesor/dictados/{uuid.uuid4()}/padron"
        )
        assert resp.status_code == 404

    async def test_get_padron_sin_permiso_403(
        self, app, client: AsyncClient, db_session: AsyncSession, test_tenant,
        auth_user_no_perm
    ):
        """TRIANGULATE: usuario sin padron:gestionar-alumno → 403 (fail-closed)."""
        from tests.helpers import cleanup_permission_cache as _cleanup

        async def _override_no_perm():
            return auth_user_no_perm

        app.dependency_overrides[get_current_user] = _override_no_perm
        _cleanup()
        try:
            resp = await client.get(
                f"/api/v1/profesor/dictados/{uuid.uuid4()}/padron"
            )
            assert resp.status_code == 403
        finally:
            _cleanup()

    async def test_get_padron_tenant_isolation_404(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, another_tenant, auth_user
    ):
        """TRIANGULATE: padrón de otro tenant → 404 (tenant isolation)."""
        d = await _create_full_dictado(db_session, another_tenant.id, auth_user.user_id)

        resp = await client.get(
            f"/api/v1/profesor/dictados/{d['dictado'].id}/padron"
        )
        assert resp.status_code == 404


class TestAlumnosDisponibles:
    """Integration tests for GET /api/v1/profesor/dictados/{id}/alumnos-disponibles.

    TDD: RED → GREEN → TRIANGULATE.
    """

    async def test_alumnos_disponibles_retorna_alumnos_del_tenant(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """GREEN: endpoint lista alumnos del tenant que no están en el padrón."""
        d = await _create_full_dictado(db_session, test_tenant.id, auth_user.user_id)

        # Create a tenant User + Usuario with ALUMNO role
        user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
        alumno_user = await user_repo.create(
            {
                "email": f"alumno-disp-{uuid.uuid4().hex[:6]}@test.com",
                "password_hash": "hash",
                "display_name": "Disponible",
                "is_active": True,
                "roles": ["ALUMNO"],
            }
        )
        from app.models.usuario import Usuario as UsuarioModel
        u_repo = BaseRepository(model=UsuarioModel, session=db_session, tenant_id=test_tenant.id)
        alumno_usuario = await u_repo.create(
            {
                "user_id": alumno_user.id,
                "nombre": "Alice",
                "apellidos": "Disponible",
                "estado": "Activo",
                "facturador": False,
            }
        )
        from app.models.asignacion import Asignacion as AsignacionModel
        asig_repo = BaseRepository(model=AsignacionModel, session=db_session, tenant_id=test_tenant.id)
        await asig_repo.create(
            {
                "usuario_id": alumno_usuario.id,
                "rol": "ALUMNO",
                "desde": datetime.date.today(),
                "hasta": None,
            }
        )

        resp = await client.get(
            f"/api/v1/profesor/dictados/{d['dictado'].id}/alumnos-disponibles"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        ids = [item["usuario_id"] for item in data]
        assert str(alumno_usuario.id) in ids

    async def test_alumnos_disponibles_excluye_ya_en_padron(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """TRIANGULATE: alumno ya en el padrón (vía usuario_id) no aparece."""
        d = await _create_full_dictado(db_session, test_tenant.id, auth_user.user_id)

        # Create alumno and link them to the padron via usuario_id
        user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
        alumno_user = await user_repo.create(
            {
                "email": f"alumno-pad-{uuid.uuid4().hex[:6]}@test.com",
                "password_hash": "hash",
                "display_name": "InPadron",
                "is_active": True,
                "roles": ["ALUMNO"],
            }
        )
        from app.models.usuario import Usuario as UsuarioModel
        u_repo = BaseRepository(model=UsuarioModel, session=db_session, tenant_id=test_tenant.id)
        alumno_usuario = await u_repo.create(
            {
                "user_id": alumno_user.id,
                "nombre": "Bob",
                "apellidos": "InPadron",
                "estado": "Activo",
                "facturador": False,
            }
        )
        from app.models.asignacion import Asignacion as AsignacionModel
        asig_repo = BaseRepository(model=AsignacionModel, session=db_session, tenant_id=test_tenant.id)
        await asig_repo.create(
            {
                "usuario_id": alumno_usuario.id,
                "rol": "ALUMNO",
                "desde": datetime.date.today(),
                "hasta": None,
            }
        )

        # Add this alumno to the padron (with usuario_id linked)
        ep_repo = BaseRepository(model=EntradaPadron, session=db_session, tenant_id=test_tenant.id)
        await ep_repo.create(
            {
                "version_id": d["version"].id,
                "usuario_id": alumno_usuario.id,
                "nombre": "Bob",
                "apellidos": "InPadron",
            }
        )

        resp = await client.get(
            f"/api/v1/profesor/dictados/{d['dictado'].id}/alumnos-disponibles"
        )
        assert resp.status_code == 200
        data = resp.json()
        ids = [item["usuario_id"] for item in data]
        assert str(alumno_usuario.id) not in ids

    async def test_alumnos_disponibles_sin_permiso_403(
        self, app, client: AsyncClient, db_session: AsyncSession, test_tenant,
        auth_user_no_perm
    ):
        """TRIANGULATE: sin padron:gestionar-alumno → 403."""
        from tests.helpers import cleanup_permission_cache as _cleanup

        async def _override_no_perm():
            return auth_user_no_perm

        app.dependency_overrides[get_current_user] = _override_no_perm
        _cleanup()
        try:
            resp = await client.get(
                f"/api/v1/profesor/dictados/{uuid.uuid4()}/alumnos-disponibles"
            )
            assert resp.status_code == 403
        finally:
            _cleanup()


class TestAltaAlumnoConUsuarioId:
    """Integration tests for POST alta-alumno with usuario_id primary path.

    TDD: RED → GREEN → TRIANGULATE.
    """

    async def test_alta_con_usuario_id_retorna_201(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """GREEN: POST con usuario_id válido crea entrada y devuelve 201."""
        d = await _create_full_dictado(db_session, test_tenant.id, auth_user.user_id)

        # Create a Usuario to add
        user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
        alumno_user = await user_repo.create(
            {
                "email": f"new-alumno-{uuid.uuid4().hex[:6]}@test.com",
                "password_hash": "hash",
                "display_name": "New",
                "is_active": True,
                "roles": ["ALUMNO"],
            }
        )
        from app.models.usuario import Usuario as UsuarioModel
        u_repo = BaseRepository(model=UsuarioModel, session=db_session, tenant_id=test_tenant.id)
        alumno_usuario = await u_repo.create(
            {
                "user_id": alumno_user.id,
                "nombre": "Carlos",
                "apellidos": "Nuevo",
                "estado": "Activo",
                "facturador": False,
            }
        )

        resp = await client.post(
            f"/api/v1/profesor/dictados/{d['dictado'].id}/padron/alumnos",
            json={"usuario_id": str(alumno_usuario.id)},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["nombre"] == "Carlos"
        assert data["apellidos"] == "Nuevo"

    async def test_alta_con_usuario_id_idempotente_409(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """TRIANGULATE: añadir el mismo usuario_id dos veces → 409."""
        d = await _create_full_dictado(db_session, test_tenant.id, auth_user.user_id)

        user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
        alumno_user = await user_repo.create(
            {
                "email": f"dup-{uuid.uuid4().hex[:6]}@test.com",
                "password_hash": "hash",
                "display_name": "Dup",
                "is_active": True,
                "roles": ["ALUMNO"],
            }
        )
        from app.models.usuario import Usuario as UsuarioModel
        u_repo = BaseRepository(model=UsuarioModel, session=db_session, tenant_id=test_tenant.id)
        alumno_usuario = await u_repo.create(
            {
                "user_id": alumno_user.id,
                "nombre": "Dup",
                "apellidos": "Alumno",
                "estado": "Activo",
                "facturador": False,
            }
        )

        # Add via usuario_id first time: link to padron
        ep_repo = BaseRepository(model=EntradaPadron, session=db_session, tenant_id=test_tenant.id)
        await ep_repo.create(
            {
                "version_id": d["version"].id,
                "usuario_id": alumno_usuario.id,
                "nombre": "Dup",
                "apellidos": "Alumno",
            }
        )

        resp = await client.post(
            f"/api/v1/profesor/dictados/{d['dictado'].id}/padron/alumnos",
            json={"usuario_id": str(alumno_usuario.id)},
        )
        assert resp.status_code == 409

    async def test_alta_sin_usuario_id_ni_nombre_422(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """TRIANGULATE: body sin usuario_id y sin nombre → 422."""
        d = await _create_full_dictado(db_session, test_tenant.id, auth_user.user_id)
        resp = await client.post(
            f"/api/v1/profesor/dictados/{d['dictado'].id}/padron/alumnos",
            json={},
        )
        assert resp.status_code == 422

    async def test_alta_usuario_id_inexistente_404(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """TRIANGULATE: usuario_id que no existe en el tenant → 404."""
        d = await _create_full_dictado(db_session, test_tenant.id, auth_user.user_id)
        resp = await client.post(
            f"/api/v1/profesor/dictados/{d['dictado'].id}/padron/alumnos",
            json={"usuario_id": str(uuid.uuid4())},
        )
        assert resp.status_code == 404


class TestCalificacionesConActividadId:
    """Integration tests for GET /api/admin/calificaciones/dictados/{id}.

    Verifies that `actividad_id` is now included in the response.
    """

    async def test_listar_calificaciones_incluye_actividad_id(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """GREEN: calificaciones incluyen actividad_id (puede ser None para legacy)."""
        d = await _create_full_dictado(db_session, test_tenant.id, auth_user.user_id)
        entrada = d["entradas"][0]

        calif_repo = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
        await calif_repo.create(
            {
                "entrada_padron_id": entrada.id,
                "dictado_id": d["dictado"].id,
                "actividad": "TP1",
                "nota_numerica": 7.0,
                "aprobado": True,
                "origen": "Manual",
                # actividad_id not set — legacy row
            }
        )

        resp = await client.get(
            f"/api/admin/calificaciones/dictados/{d['dictado'].id}"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        row = data[0]
        assert "actividad" in row
        assert row["actividad"] == "TP1"
        # actividad_id is present in the response (may be None for legacy rows)
        assert "actividad_id" in row
        assert row["actividad_id"] is None  # no actividad entity linked

    async def test_listar_calificaciones_con_actividad_id_enlazado(
        self, client: AsyncClient, db_session: AsyncSession, test_tenant, auth_user
    ):
        """TRIANGULATE: calificación enlazada a Actividad entity incluye actividad_id."""
        from app.models.actividad import Actividad

        d = await _create_full_dictado(db_session, test_tenant.id, auth_user.user_id)
        entrada = d["entradas"][0]

        # Create Actividad entity first
        act_repo = BaseRepository(model=Actividad, session=db_session, tenant_id=test_tenant.id)
        actividad = await act_repo.create(
            {
                "nombre": "TP2",
                "tipo": "TP",
                "dictado_id": d["dictado"].id,
                "fecha_limite": None,
            }
        )

        calif_repo = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
        await calif_repo.create(
            {
                "entrada_padron_id": entrada.id,
                "dictado_id": d["dictado"].id,
                "actividad": "TP2",
                "actividad_id": actividad.id,
                "nota_numerica": 9.0,
                "aprobado": True,
                "origen": "Importado",
            }
        )

        resp = await client.get(
            f"/api/admin/calificaciones/dictados/{d['dictado'].id}"
        )
        assert resp.status_code == 200
        data = resp.json()
        row = next(r for r in data if r["actividad"] == "TP2")
        assert row["actividad_id"] == str(actividad.id)
