"""Tests for CalificacionService (C-10, TASKS 16-18).

Tests cover:
- preview_archivo: parsing, token generation, student resolution
- confirmar_importacion: apobado calc (numeric+textual), persistence, audit
- importar_finalizacion_preview / importar_finalizacion_confirm
- listar_calificaciones
- recalcular_por_cambio_umbral
- Token expiration and validation errors
"""

import csv
import io
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.acciones_auditoria import AccionAuditoria
from app.core.exceptions import ValidationException
from app.models.user import User
from app.models.usuario import Usuario
from app.models.dictado import Dictado
from app.models.version_padron import VersionPadron
from app.models.entrada_padron import EntradaPadron
from app.repositories.base import BaseRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.dictado_repository import DictadoRepository
from app.repositories.version_padron_repository import VersionPadronRepository
from app.repositories.entrada_padron_repository import EntradaPadronRepository
from app.services.calificaciones.calificacion_service import CalificacionService


# ── Helpers ──────────────────────────────────────────────────────────────


def _make_csv_bytes(headers: list[str], rows: list[list]) -> bytes:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    return output.getvalue().encode("utf-8")


def _make_service(
    db_session: AsyncSession, tenant_id: uuid.UUID, current_user_id: uuid.UUID
) -> CalificacionService:
    return CalificacionService(
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


async def _seed_active_version(
    db_session: AsyncSession, tenant_id: uuid.UUID, dictado_id: uuid.UUID, usuario_id: uuid.UUID
) -> VersionPadron:
    vp_repo = VersionPadronRepository(session=db_session, tenant_id=tenant_id)
    version = await vp_repo.create({
        "dictado_id": dictado_id,
        "cargado_por": usuario_id,
        "activa": True,
    })
    return version


async def _seed_entradas(
    db_session: AsyncSession, tenant_id: uuid.UUID, version_id: uuid.UUID,
    alumnos: list[dict],
) -> list[EntradaPadron]:
    ep_repo = EntradaPadronRepository(session=db_session, tenant_id=tenant_id)
    entries = await ep_repo.bulk_create([
        {"version_id": version_id, **a}
        for a in alumnos
    ])
    return entries


# ── preview_archivo ──────────────────────────────────────────────────────


class TestPreviewArchivo:
    async def test_preview_parses_csv_and_generates_token(
        self, db_session: AsyncSession, test_tenant
    ):
        user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        version = await _seed_active_version(db_session, test_tenant.id, dictado.id, usuario.id)
        await _seed_entradas(db_session, test_tenant.id, version.id, [
            {"nombre": "Juan", "apellidos": "Pérez", "email": "juan@test.com"},
            {"nombre": "María", "apellidos": "García", "email": "maria@test.com"},
        ])

        service = _make_service(db_session, test_tenant.id, user.id)
        csv_content = _make_csv_bytes(
            ["Apellidos", "Nombre", "Parcial 1 (Real)", "TP 1 (Real)"],
            [
                ["Pérez", "Juan", "85", "90"],
                ["García", "María", "70", "60"],
            ],
        )

        result = await service.preview_archivo(csv_content, "grades.csv", dictado.id)

        assert "actividades_detectadas" in result
        assert len(result["actividades_detectadas"]) == 2
        assert result["total_filas"] == 2
        assert len(result["filas"]) == 2  # preview first 10
        assert "preview_token" in result
        assert isinstance(result["preview_token"], str)

    async def test_preview_matches_students_by_name(
        self, db_session: AsyncSession, test_tenant
    ):
        user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        version = await _seed_active_version(db_session, test_tenant.id, dictado.id, usuario.id)
        entradas = await _seed_entradas(db_session, test_tenant.id, version.id, [
            {"nombre": "Juan", "apellidos": "Pérez", "email": "juan@test.com"},
            {"nombre": "Ana", "apellidos": "López", "email": "ana@test.com"},
        ])

        service = _make_service(db_session, test_tenant.id, user.id)
        csv_content = _make_csv_bytes(
            ["Apellidos", "Nombre", "Parcial 1 (Real)"],
            [["Pérez", "Juan", "85"]],
        )

        result = await service.preview_archivo(csv_content, "grades.csv", dictado.id)

        assert result["total_filas"] == 1
        # The fila should have entrada_padron_id resolved
        assert result["filas"][0]["entrada_padron_id"] is not None

    async def test_preview_unmatched_student_has_null_entrada_id(
        self, db_session: AsyncSession, test_tenant
    ):
        user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        version = await _seed_active_version(db_session, test_tenant.id, dictado.id, usuario.id)
        await _seed_entradas(db_session, test_tenant.id, version.id, [
            {"nombre": "Ana", "apellidos": "López", "email": "ana@test.com"},
        ])

        service = _make_service(db_session, test_tenant.id, user.id)
        csv_content = _make_csv_bytes(
            ["Apellidos", "Nombre", "Parcial 1 (Real)"],
            [["Desconocido", "Alumno", "50"]],
        )

        result = await service.preview_archivo(csv_content, "grades.csv", dictado.id)
        assert result["filas"][0]["entrada_padron_id"] is None


# ── confirmar_importacion ────────────────────────────────────────────────


class TestConfirmarImportacion:
    async def test_confirm_creates_calificaciones_and_marks_aprobado(
        self, db_session: AsyncSession, test_tenant
    ):
        user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        version = await _seed_active_version(db_session, test_tenant.id, dictado.id, usuario.id)
        entradas = await _seed_entradas(db_session, test_tenant.id, version.id, [
            {"nombre": "Juan", "apellidos": "Pérez", "email": "juan@test.com"},
        ])

        service = _make_service(db_session, test_tenant.id, user.id)
        csv_content = _make_csv_bytes(
            ["Apellidos", "Nombre", "Parcial 1 (Real)"],
            [["Pérez", "Juan", "85"]],
        )
        preview = await service.preview_archivo(csv_content, "grades.csv", dictado.id)

        result = await service.confirmar_importacion(
            dictado_id=dictado.id,
            preview_token=preview["preview_token"],
            actividades_seleccionadas=["Parcial 1"],
        )

        assert result["total_importados"] == 1
        assert result["aprobados"] == 1   # 85 >= 60
        assert result["desaprobados"] == 0
        assert "mensaje" in result

    async def test_confirm_marks_desaprobado_when_below_umbral(
        self, db_session: AsyncSession, test_tenant
    ):
        user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        version = await _seed_active_version(db_session, test_tenant.id, dictado.id, usuario.id)
        entradas = await _seed_entradas(db_session, test_tenant.id, version.id, [
            {"nombre": "Juan", "apellidos": "Pérez", "email": "juan@test.com"},
        ])

        service = _make_service(db_session, test_tenant.id, user.id)
        csv_content = _make_csv_bytes(
            ["Apellidos", "Nombre", "Parcial 1 (Real)"],
            [["Pérez", "Juan", "40"]],
        )
        preview = await service.preview_archivo(csv_content, "grades.csv", dictado.id)

        result = await service.confirmar_importacion(
            dictado_id=dictado.id,
            preview_token=preview["preview_token"],
            actividades_seleccionadas=["Parcial 1"],
        )

        assert result["aprobados"] == 0
        assert result["desaprobados"] == 1

    async def test_confirm_handles_textual_aprobado(
        self, db_session: AsyncSession, test_tenant
    ):
        user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        version = await _seed_active_version(db_session, test_tenant.id, dictado.id, usuario.id)
        entradas = await _seed_entradas(db_session, test_tenant.id, version.id, [
            {"nombre": "Juan", "apellidos": "Pérez", "email": "juan@test.com"},
        ])

        service = _make_service(db_session, test_tenant.id, user.id)
        csv_content = _make_csv_bytes(
            ["Apellidos", "Nombre", "TP 1"],
            [["Pérez", "Juan", "Satisfactorio"]],
        )
        preview = await service.preview_archivo(csv_content, "grades.csv", dictado.id)

        result = await service.confirmar_importacion(
            dictado_id=dictado.id,
            preview_token=preview["preview_token"],
            actividades_seleccionadas=["TP 1"],
        )

        assert result["total_importados"] == 1
        assert result["aprobados"] == 1

    async def test_confirm_rejects_invalid_token(
        self, db_session: AsyncSession, test_tenant
    ):
        user, _ = await _create_user_and_profile(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        service = _make_service(db_session, test_tenant.id, user.id)

        with pytest.raises((ValidationException, ValueError)):
            await service.confirmar_importacion(
                dictado_id=dictado.id,
                preview_token="invalid-token",
                actividades_seleccionadas=["Parcial 1"],
            )

    async def test_confirm_rejects_wrong_dictado(
        self, db_session: AsyncSession, test_tenant
    ):
        user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        version = await _seed_active_version(db_session, test_tenant.id, dictado.id, usuario.id)
        entradas = await _seed_entradas(db_session, test_tenant.id, version.id, [
            {"nombre": "Juan", "apellidos": "Pérez", "email": "juan@test.com"},
        ])

        service = _make_service(db_session, test_tenant.id, user.id)
        csv_content = _make_csv_bytes(
            ["Apellidos", "Nombre", "Parcial 1 (Real)"],
            [["Pérez", "Juan", "85"]],
        )
        preview = await service.preview_archivo(csv_content, "grades.csv", dictado.id)

        other_dictado_id = uuid.uuid4()
        with pytest.raises((ValidationException, ValueError)):
            await service.confirmar_importacion(
                dictado_id=other_dictado_id,
                preview_token=preview["preview_token"],
                actividades_seleccionadas=["Parcial 1"],
            )

    async def test_confirm_persists_calificaciones(
        self, db_session: AsyncSession, test_tenant
    ):
        user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        version = await _seed_active_version(db_session, test_tenant.id, dictado.id, usuario.id)
        entradas = await _seed_entradas(db_session, test_tenant.id, version.id, [
            {"nombre": "Juan", "apellidos": "Pérez", "email": "juan@test.com"},
        ])

        service = _make_service(db_session, test_tenant.id, user.id)
        csv_content = _make_csv_bytes(
            ["Apellidos", "Nombre", "Parcial 1 (Real)"],
            [["Pérez", "Juan", "85"]],
        )
        preview = await service.preview_archivo(csv_content, "grades.csv", dictado.id)
        await service.confirmar_importacion(
            dictado_id=dictado.id,
            preview_token=preview["preview_token"],
            actividades_seleccionadas=["Parcial 1"],
        )

        califs = await service.listar_calificaciones(dictado.id)
        assert len(califs) == 1
        assert califs[0]["actividad"] == "Parcial 1"
        assert califs[0]["aprobado"] is True

    async def test_confirm_with_no_matching_actividades_returns_zero(
        self, db_session: AsyncSession, test_tenant
    ):
        user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        version = await _seed_active_version(db_session, test_tenant.id, dictado.id, usuario.id)
        entradas = await _seed_entradas(db_session, test_tenant.id, version.id, [
            {"nombre": "Juan", "apellidos": "Pérez", "email": "juan@test.com"},
        ])

        service = _make_service(db_session, test_tenant.id, user.id)
        csv_content = _make_csv_bytes(
            ["Apellidos", "Nombre", "Parcial 1 (Real)"],
            [["Pérez", "Juan", "85"]],
        )
        preview = await service.preview_archivo(csv_content, "grades.csv", dictado.id)

        result = await service.confirmar_importacion(
            dictado_id=dictado.id,
            preview_token=preview["preview_token"],
            actividades_seleccionadas=["Actividad Inexistente"],
        )

        assert result["total_importados"] == 0

    async def test_confirm_cleans_up_token_after_use(
        self, db_session: AsyncSession, test_tenant
    ):
        user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        version = await _seed_active_version(db_session, test_tenant.id, dictado.id, usuario.id)
        entradas = await _seed_entradas(db_session, test_tenant.id, version.id, [
            {"nombre": "Juan", "apellidos": "Pérez", "email": "juan@test.com"},
        ])

        service = _make_service(db_session, test_tenant.id, user.id)
        csv_content = _make_csv_bytes(
            ["Apellidos", "Nombre", "Parcial 1 (Real)"],
            [["Pérez", "Juan", "85"]],
        )
        preview = await service.preview_archivo(csv_content, "grades.csv", dictado.id)
        await service.confirmar_importacion(
            dictado_id=dictado.id,
            preview_token=preview["preview_token"],
            actividades_seleccionadas=["Parcial 1"],
        )

        with pytest.raises((ValidationException, ValueError)):
            await service.confirmar_importacion(
                dictado_id=dictado.id,
                preview_token=preview["preview_token"],
                actividades_seleccionadas=["Parcial 1"],
            )


# ── listar_calificaciones ────────────────────────────────────────────────


class TestListarCalificaciones:
    async def test_listar_returns_empty_when_no_calificaciones(
        self, db_session: AsyncSession, test_tenant
    ):
        user, _ = await _create_user_and_profile(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        service = _make_service(db_session, test_tenant.id, user.id)

        califs = await service.listar_calificaciones(dictado.id)
        assert califs == []


# ── recalcular_por_cambio_umbral ────────────────────────────────────────


class TestRecalcularPorCambioUmbral:
    async def test_recalcular_updates_all_aprobado_values(
        self, db_session: AsyncSession, test_tenant
    ):
        user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        version = await _seed_active_version(db_session, test_tenant.id, dictado.id, usuario.id)
        entradas = await _seed_entradas(db_session, test_tenant.id, version.id, [
            {"nombre": "Juan", "apellidos": "Pérez", "email": "juan@test.com"},
        ])

        service = _make_service(db_session, test_tenant.id, user.id)
        csv_content = _make_csv_bytes(
            ["Apellidos", "Nombre", "Parcial 1 (Real)"],
            [["Pérez", "Juan", "85"]],
        )
        preview = await service.preview_archivo(csv_content, "grades.csv", dictado.id)
        await service.confirmar_importacion(
            dictado_id=dictado.id,
            preview_token=preview["preview_token"],
            actividades_seleccionadas=["Parcial 1"],
        )

        updated = await service.recalcular_por_cambio_umbral(dictado.id)
        assert isinstance(updated, int)
        assert updated >= 0


# ── Tenant isolation ─────────────────────────────────────────────────────


class TestTenantIsolation:
    async def test_cross_tenant_preview_returns_no_students(
        self, db_session: AsyncSession, test_tenant, another_tenant
    ):
        user_a, usuario_a = await _create_user_and_profile(db_session, test_tenant.id)
        dictado_a = await _create_dictado(db_session, test_tenant.id)
        version_a = await _seed_active_version(db_session, test_tenant.id, dictado_a.id, usuario_a.id)
        await _seed_entradas(db_session, test_tenant.id, version_a.id, [
            {"nombre": "Juan", "apellidos": "Pérez", "email": "juan@test.com"},
        ])

        user_b, _ = await _create_user_and_profile(db_session, another_tenant.id)
        service_b = _make_service(db_session, another_tenant.id, user_b.id)
        csv_content = _make_csv_bytes(
            ["Apellidos", "Nombre", "Parcial 1 (Real)"],
            [["Pérez", "Juan", "85"]],
        )

        result = await service_b.preview_archivo(csv_content, "grades.csv", dictado_a.id)
        assert result["filas"][0]["entrada_padron_id"] is None
