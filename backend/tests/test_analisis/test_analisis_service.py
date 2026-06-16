import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asignacion import Asignacion
from app.models.calificacion import Calificacion
from app.models.dictado import Dictado
from app.models.entrada_padron import EntradaPadron
from app.models.umbral_materia import UmbralMateria
from app.models.usuario import Usuario
from app.models.user import User
from app.models.version_padron import VersionPadron
from app.repositories.base import BaseRepository
from app.repositories.dictado_repository import DictadoRepository
from app.repositories.entrada_padron_repository import EntradaPadronRepository
from app.services.analisis.analisis_service import AnalisisService


# ─── Helpers ──────────────────────────────────────────────────────────────


async def _create_dictado(db_session: AsyncSession, tenant_id: uuid.UUID) -> Dictado:
    from app.models.carrera import Carrera
    from app.models.cohorte import Cohorte
    from app.models.materia import Materia
    c_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=tenant_id)
    carrera = await c_repo.create({"codigo": "ING-INF", "nombre": "Ingeniería Informática"})
    m_repo = BaseRepository(model=Materia, session=db_session, tenant_id=tenant_id)
    materia = await m_repo.create({"codigo": "MAT-101", "nombre": "Análisis Matemático I"})
    co_repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=tenant_id)
    cohorte = await co_repo.create({"carrera_id": carrera.id, "nombre": "2024", "anio": 2024})
    repo = DictadoRepository(session=db_session, tenant_id=tenant_id)
    return await repo.create(
        {"materia_id": materia.id, "carrera_id": carrera.id, "cohorte_id": cohorte.id}
    )


async def _create_usuario(
    db_session: AsyncSession, tenant_id: uuid.UUID,
) -> tuple[User, Usuario]:
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=tenant_id)
    user = await user_repo.create({
        "email": f"user-{uuid.uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "Test User",
        "is_active": True,
        "roles": ["PROFESOR"],
    })
    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=tenant_id)
    usuario = await usuario_repo.create({
        "user_id": user.id,
        "nombre": "Test",
        "apellidos": "User",
        "estado": "Activo",
    })
    return user, usuario


async def _create_version_entradas(
    db_session: AsyncSession, tenant_id: uuid.UUID, dictado_id: uuid.UUID, usuario_id: uuid.UUID,
    alumnos: list[dict],
) -> list[EntradaPadron]:
    vp_repo = BaseRepository(model=VersionPadron, session=db_session, tenant_id=tenant_id)
    version = await vp_repo.create({"dictado_id": dictado_id, "cargado_por": usuario_id, "activa": True})
    ep_repo = EntradaPadronRepository(session=db_session, tenant_id=tenant_id)
    return await ep_repo.bulk_create([
        {"version_id": version.id, **a} for a in alumnos
    ])


async def _create_calificaciones(
    db_session: AsyncSession, tenant_id: uuid.UUID,
    entries: list[dict],
):
    from app.repositories.calificacion_repository import CalificacionRepository
    repo = CalificacionRepository(session=db_session, tenant_id=tenant_id)
    return await repo.bulk_create(entries)


async def _make_service(
    db_session: AsyncSession, tenant_id: uuid.UUID, usuario: Usuario,
) -> AnalisisService:
    return AnalisisService(db_session=db_session, tenant_id=tenant_id, current_user_id=usuario.user_id)


# ─── Tests ────────────────────────────────────────────────────────────────


class TestGetAlumnosAtrasados:
    async def test_happy_path(self, db_session: AsyncSession, test_tenant):
        user, usuario = await _create_usuario(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        entradas = await _create_version_entradas(
            db_session, test_tenant.id, dictado.id, usuario.id,
            [
                {"nombre": "Juan", "apellidos": "Pérez"},
                {"nombre": "María", "apellidos": "García"},
            ],
        )
        await _create_calificaciones(db_session, test_tenant.id, [
            {"entrada_padron_id": entradas[0].id, "dictado_id": dictado.id, "actividad": "P1", "nota_numerica": 80, "aprobado": True},
            {"entrada_padron_id": entradas[0].id, "dictado_id": dictado.id, "actividad": "P2", "nota_numerica": 90, "aprobado": True},
            {"entrada_padron_id": entradas[1].id, "dictado_id": dictado.id, "actividad": "P1", "nota_numerica": 40, "aprobado": False},
        ])
        service = await _make_service(db_session, test_tenant.id, usuario)
        result = await service.get_alumnos_atrasados(dictado.id)
        assert len(result) == 1
        assert result[0]["alumno_apellido"] == "García"

    async def test_no_atrasados(self, db_session: AsyncSession, test_tenant):
        user, usuario = await _create_usuario(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        entradas = await _create_version_entradas(
            db_session, test_tenant.id, dictado.id, usuario.id,
            [{"nombre": "Juan", "apellidos": "Pérez"}],
        )
        await _create_calificaciones(db_session, test_tenant.id, [
            {"entrada_padron_id": entradas[0].id, "dictado_id": dictado.id, "actividad": "P1", "nota_numerica": 80, "aprobado": True},
        ])
        service = await _make_service(db_session, test_tenant.id, usuario)
        result = await service.get_alumnos_atrasados(dictado.id)
        assert result == []

    async def test_empty_dictado_returns_empty(self, db_session: AsyncSession, test_tenant):
        user, usuario = await _create_usuario(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        service = await _make_service(db_session, test_tenant.id, usuario)
        result = await service.get_alumnos_atrasados(dictado.id)
        assert result == []


class TestGetRankingAprobadas:
    async def test_happy_path(self, db_session: AsyncSession, test_tenant):
        user, usuario = await _create_usuario(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        entradas = await _create_version_entradas(
            db_session, test_tenant.id, dictado.id, usuario.id,
            [
                {"nombre": "Juan", "apellidos": "Pérez"},
                {"nombre": "María", "apellidos": "García"},
            ],
        )
        await _create_calificaciones(db_session, test_tenant.id, [
            {"entrada_padron_id": entradas[0].id, "dictado_id": dictado.id, "actividad": "P1", "nota_numerica": 80, "aprobado": True},
            {"entrada_padron_id": entradas[0].id, "dictado_id": dictado.id, "actividad": "P2", "nota_numerica": 90, "aprobado": True},
            {"entrada_padron_id": entradas[1].id, "dictado_id": dictado.id, "actividad": "P1", "nota_numerica": 40, "aprobado": False},
        ])
        service = await _make_service(db_session, test_tenant.id, usuario)
        result = await service.get_ranking_aprobadas(dictado.id)
        assert len(result) == 1  # Only Juan has aprobadas
        assert result[0]["aprobadas"] == 2

    async def test_empty_ranking(self, db_session: AsyncSession, test_tenant):
        user, usuario = await _create_usuario(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        service = await _make_service(db_session, test_tenant.id, usuario)
        result = await service.get_ranking_aprobadas(dictado.id)
        assert result == []


class TestGetReporteMateria:
    async def test_happy_path(self, db_session: AsyncSession, test_tenant):
        user, usuario = await _create_usuario(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        entradas = await _create_version_entradas(
            db_session, test_tenant.id, dictado.id, usuario.id,
            [
                {"nombre": "Juan", "apellidos": "Pérez"},
                {"nombre": "María", "apellidos": "García"},
            ],
        )
        await _create_calificaciones(db_session, test_tenant.id, [
            {"entrada_padron_id": entradas[0].id, "dictado_id": dictado.id, "actividad": "P1", "nota_numerica": 80, "aprobado": True},
            {"entrada_padron_id": entradas[0].id, "dictado_id": dictado.id, "actividad": "P2", "nota_numerica": 90, "aprobado": True},
            {"entrada_padron_id": entradas[1].id, "dictado_id": dictado.id, "actividad": "P1", "nota_numerica": 40, "aprobado": False},
        ])
        service = await _make_service(db_session, test_tenant.id, usuario)
        result = await service.get_reporte_materia(dictado.id)
        assert result["total_alumnos"] == 2
        assert result["aprobados"] == 1
        assert result["atrasados"] == 1
        assert result["total_actividades"] == 2

    async def test_empty_reporte(self, db_session: AsyncSession, test_tenant):
        user, usuario = await _create_usuario(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        service = await _make_service(db_session, test_tenant.id, usuario)
        result = await service.get_reporte_materia(dictado.id)
        assert result["sin_datos"] is True


class TestGetNotasFinales:
    async def test_happy_path(self, db_session: AsyncSession, test_tenant):
        user, usuario = await _create_usuario(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        entradas = await _create_version_entradas(
            db_session, test_tenant.id, dictado.id, usuario.id,
            [{"nombre": "Juan", "apellidos": "Pérez"}],
        )
        await _create_calificaciones(db_session, test_tenant.id, [
            {"entrada_padron_id": entradas[0].id, "dictado_id": dictado.id, "actividad": "P1", "nota_numerica": 80, "aprobado": True},
            {"entrada_padron_id": entradas[0].id, "dictado_id": dictado.id, "actividad": "P2", "nota_numerica": 90, "aprobado": True},
        ])
        service = await _make_service(db_session, test_tenant.id, usuario)
        result = await service.get_notas_finales(dictado.id)
        assert len(result) == 1
        assert result[0]["nota_final"] == 85.0

    async def test_no_notas_returns_null(self, db_session: AsyncSession, test_tenant):
        user, usuario = await _create_usuario(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        entradas = await _create_version_entradas(
            db_session, test_tenant.id, dictado.id, usuario.id,
            [{"nombre": "Juan", "apellidos": "Pérez"}],
        )
        await _create_calificaciones(db_session, test_tenant.id, [
            {"entrada_padron_id": entradas[0].id, "dictado_id": dictado.id, "actividad": "TP 1", "nota_textual": "Satisfactorio", "aprobado": True},
        ])
        service = await _make_service(db_session, test_tenant.id, usuario)
        result = await service.get_notas_finales(dictado.id)
        assert len(result) == 1
        assert result[0]["nota_final"] is None


class TestGetTPSinCorregir:
    async def test_requires_finalizaciones(self, db_session: AsyncSession, test_tenant):
        user, usuario = await _create_usuario(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        service = await _make_service(db_session, test_tenant.id, usuario)
        with pytest.raises(ValueError, match="finalizaci[óo]n"):
            await service.get_tps_sin_corregir(dictado.id, [])


class TestMonitorGeneral:
    async def test_basic(self, db_session: AsyncSession, test_tenant):
        user, usuario = await _create_usuario(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        entradas = await _create_version_entradas(
            db_session, test_tenant.id, dictado.id, usuario.id,
            [{"nombre": "Juan", "apellidos": "Pérez"}],
        )
        await _create_calificaciones(db_session, test_tenant.id, [
            {"entrada_padron_id": entradas[0].id, "dictado_id": dictado.id, "actividad": "P1", "nota_numerica": 80, "aprobado": True},
        ])
        service = await _make_service(db_session, test_tenant.id, usuario)
        result = await service.get_monitor_general(dictado_id=dictado.id)
        assert result["total_count"] == 1
        assert len(result["items"]) == 1
        assert result["items"][0]["actividades_aprobadas"] == 1

    async def test_empty(self, db_session: AsyncSession, test_tenant):
        user, usuario = await _create_usuario(db_session, test_tenant.id)
        service = await _make_service(db_session, test_tenant.id, usuario)
        result = await service.get_monitor_general()
        assert result["total_count"] == 0
        assert result["items"] == []
