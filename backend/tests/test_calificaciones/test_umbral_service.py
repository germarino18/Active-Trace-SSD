"""Tests for UmbralService (C-10, TASKS 24-26).

Tests cover:
- obtener_umbral: custom threshold vs default fallback
- configurar_umbral: create, update, recalculate
- configurar_umbral: invalid values, no asignacion
- obtener_umbral without asignacion (defaults)
"""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationException
from app.models.asignacion import Asignacion
from app.models.dictado import Dictado
from app.models.user import User
from app.models.usuario import Usuario
from app.repositories.base import BaseRepository
from app.repositories.dictado_repository import DictadoRepository
from app.services.calificaciones.umbral_service import UmbralService


def _make_service(
    db_session: AsyncSession, tenant_id: uuid.UUID, current_user_id: uuid.UUID
) -> UmbralService:
    return UmbralService(
        db_session=db_session,
        tenant_id=tenant_id,
        current_user_id=current_user_id,
    )


async def _create_user_and_profile(
    db_session: AsyncSession, tenant_id: uuid.UUID,
) -> tuple[User, Usuario]:
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=tenant_id)
    user = await user_repo.create({
        "email": f"user-{uuid.uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "Test User",
        "is_active": True,
        "roles": [],
    })
    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=tenant_id)
    usuario = await usuario_repo.create({
        "user_id": user.id,
        "nombre": "Test",
        "apellidos": "User",
        "estado": "Activo",
    })
    return user, usuario


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


async def _create_asignacion(
    db_session: AsyncSession, tenant_id: uuid.UUID, usuario_id: uuid.UUID, dictado_id: uuid.UUID
) -> Asignacion:
    from datetime import date
    repo = BaseRepository(model=Asignacion, session=db_session, tenant_id=tenant_id)
    return await repo.create({
        "usuario_id": usuario_id,
        "rol": "PROFESOR",
        "dictado_id": dictado_id,
        "desde": date(2024, 1, 1),
    })


# ── obtener_umbral ───────────────────────────────────────────────────────


class TestObtenerUmbral:
    async def test_returns_defaults_when_no_asignacion(
        self, db_session: AsyncSession, test_tenant
    ):
        user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        service = _make_service(db_session, test_tenant.id, user.id)

        result = await service.obtener_umbral(dictado.id)

        assert result["umbral_pct"] == 60
        assert result["valores_aprobatorios"] == ["Satisfactorio", "Supera lo esperado"]
        assert result["es_default"] is True

    async def test_returns_defaults_when_no_umbral_config(
        self, db_session: AsyncSession, test_tenant
    ):
        user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        await _create_asignacion(db_session, test_tenant.id, usuario.id, dictado.id)
        service = _make_service(db_session, test_tenant.id, user.id)

        result = await service.obtener_umbral(dictado.id)

        assert result["es_default"] is True
        assert result["umbral_pct"] == 60

    async def test_returns_custom_umbral_when_configured(
        self, db_session: AsyncSession, test_tenant
    ):
        user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        asignacion = await _create_asignacion(db_session, test_tenant.id, usuario.id, dictado.id)
        service = _make_service(db_session, test_tenant.id, user.id)

        await service.configurar_umbral(
            dictado_id=dictado.id,
            umbral_pct=75,
            valores_aprobatorios=["Aprobado", "Promocionado"],
        )

        result = await service.obtener_umbral(dictado.id)

        assert result["umbral_pct"] == 75
        assert result["valores_aprobatorios"] == ["Aprobado", "Promocionado"]
        assert result["es_default"] is False


# ── configurar_umbral ───────────────────────────────────────────────────


class TestConfigurarUmbral:
    async def test_creates_new_umbral(
        self, db_session: AsyncSession, test_tenant
    ):
        user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        asignacion = await _create_asignacion(db_session, test_tenant.id, usuario.id, dictado.id)
        service = _make_service(db_session, test_tenant.id, user.id)

        result = await service.configurar_umbral(
            dictado_id=dictado.id,
            umbral_pct=80,
            valores_aprobatorios=["Aprobado"],
        )

        assert result["umbral_pct"] == 80
        assert result["valores_aprobatorios"] == ["Aprobado"]
        assert result["calificaciones_recalculadas"] >= 0

    async def test_updates_existing_umbral(
        self, db_session: AsyncSession, test_tenant
    ):
        user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        asignacion = await _create_asignacion(db_session, test_tenant.id, usuario.id, dictado.id)
        service = _make_service(db_session, test_tenant.id, user.id)

        first = await service.configurar_umbral(dictado.id, umbral_pct=60)
        assert first["umbral_pct"] == 60

        second = await service.configurar_umbral(
            dictado.id, umbral_pct=85, valores_aprobatorios=["Promocionado"]
        )
        assert second["umbral_pct"] == 85
        assert second["valores_aprobatorios"] == ["Promocionado"]

    async def test_recalculates_on_update(
        self, db_session: AsyncSession, test_tenant
    ):
        user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        asignacion = await _create_asignacion(db_session, test_tenant.id, usuario.id, dictado.id)

        from app.repositories.calificacion_repository import CalificacionRepository
        from app.repositories.entrada_padron_repository import EntradaPadronRepository
        from app.repositories.version_padron_repository import VersionPadronRepository

        vp_repo = VersionPadronRepository(session=db_session, tenant_id=test_tenant.id)
        version = await vp_repo.create({
            "dictado_id": dictado.id, "cargado_por": usuario.id, "activa": True,
        })
        ep_repo = EntradaPadronRepository(session=db_session, tenant_id=test_tenant.id)
        entradas = await ep_repo.bulk_create([
            {"version_id": version.id, "nombre": "Juan", "apellidos": "Pérez"},
        ])

        cal_repo = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
        await cal_repo.bulk_create([
            {"entrada_padron_id": entradas[0].id, "dictado_id": dictado.id,
             "actividad": "Parcial", "nota_numerica": 50, "aprobado": True},
            {"entrada_padron_id": entradas[0].id, "dictado_id": dictado.id,
             "actividad": "TP", "nota_numerica": 90, "aprobado": False},
        ])

        service = _make_service(db_session, test_tenant.id, user.id)
        result = await service.configurar_umbral(
            dictado.id, umbral_pct=60, valores_aprobatorios=None
        )

        assert result["calificaciones_recalculadas"] == 2

        califs = await cal_repo.find_by_dictado(dictado.id)
        califs_by_act = {c.actividad: c for c in califs}
        assert califs_by_act["Parcial"].aprobado is False  # 50 < 60
        assert califs_by_act["TP"].aprobado is True         # 90 >= 60

    async def test_rejects_invalid_umbral_pct(
        self, db_session: AsyncSession, test_tenant
    ):
        user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        asignacion = await _create_asignacion(db_session, test_tenant.id, usuario.id, dictado.id)
        service = _make_service(db_session, test_tenant.id, user.id)

        with pytest.raises((ValueError, ValidationException)):
            await service.configurar_umbral(dictado.id, umbral_pct=150)

    async def test_rejects_negative_umbral(
        self, db_session: AsyncSession, test_tenant
    ):
        user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        asignacion = await _create_asignacion(db_session, test_tenant.id, usuario.id, dictado.id)
        service = _make_service(db_session, test_tenant.id, user.id)

        with pytest.raises((ValueError, ValidationException)):
            await service.configurar_umbral(dictado.id, umbral_pct=-1)

    async def test_raises_error_when_no_asignacion(
        self, db_session: AsyncSession, test_tenant
    ):
        user, _ = await _create_user_and_profile(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        service = _make_service(db_session, test_tenant.id, user.id)

        with pytest.raises((ValidationException, ValueError)):
            await service.configurar_umbral(dictado.id, umbral_pct=60)
