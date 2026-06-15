"""Tests for `EquipoService` (C-08 task group 3).

Real ephemeral test DB (no DB mocks, regla dura #4). `current_user.id`/
`tenant_id` (NEVER a param) derive `usuario_id`/`tenant_id` (D3/D4 [SEC]).
`estado_vigencia` is derived (D3), never stored. Operaciones masivas
(masiva, clonado, vigencia) son transaccionales y emiten UN
`ASIGNACION_MODIFICAR` (D6/D7); lecturas (mis-equipos, export) NO auditan.
"""

import datetime
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.acciones_auditoria import AccionAuditoria
from app.core.exceptions import NotFoundException
from app.models.asignacion import Asignacion
from app.repositories.asignacion_repository import AsignacionRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.base import BaseRepository
from app.repositories.carrera_repository import CarreraRepository
from app.repositories.cohorte_repository import CohorteRepository
from app.repositories.materia_repository import MateriaRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.auth import CurrentUser
from app.schemas.equipo import AsignacionMasivaCreate, ClonarEquipoCreate, VigenciaEquipoUpdate
from app.services.equipo_service import EquipoService
from tests.test_equipos.conftest import make_usuario_perfil

_HOY = datetime.date.today()


def _make_request() -> Request:
    """Minimal ASGI scope so `AuditLogger.log` can read client/headers."""
    scope = {
        "type": "http",
        "client": ("127.0.0.1", 12345),
        "headers": [(b"user-agent", b"pytest")],
    }
    return Request(scope)


def _make_service(db_session: AsyncSession, tenant_id: uuid.UUID) -> EquipoService:
    return EquipoService(
        asignacion_repo=AsignacionRepository(session=db_session, tenant_id=tenant_id),
        usuario_repo=UsuarioRepository(session=db_session, tenant_id=tenant_id),
        materia_repo=MateriaRepository(session=db_session, tenant_id=tenant_id),
        carrera_repo=CarreraRepository(session=db_session, tenant_id=tenant_id),
        cohorte_repo=CohorteRepository(session=db_session, tenant_id=tenant_id),
        audit_repo=AuditLogRepository(session=db_session, tenant_id=tenant_id),
    )


async def _make_asignacion(
    db_session, tenant_id, usuario_id, rol, *, materia_id=None, carrera_id=None,
    cohorte_id=None, desde, hasta=None, responsable_id=None, comisiones=None,
):
    repo = BaseRepository(model=Asignacion, session=db_session, tenant_id=tenant_id)
    data = {
        "usuario_id": usuario_id,
        "rol": rol,
        "materia_id": materia_id,
        "carrera_id": carrera_id,
        "cohorte_id": cohorte_id,
        "desde": desde,
        "hasta": hasta,
        "responsable_id": responsable_id,
    }
    if comisiones is not None:
        data["comisiones"] = comisiones
    return await repo.create(data)


async def _make_academic_context(db_session, tenant_id, suffix):
    from app.models.carrera import Carrera
    from app.models.cohorte import Cohorte
    from app.models.materia import Materia

    materia_repo = BaseRepository(model=Materia, session=db_session, tenant_id=tenant_id)
    carrera_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=tenant_id)
    cohorte_repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=tenant_id)

    materia = await materia_repo.create({"codigo": f"MAT-{suffix}", "nombre": f"Materia {suffix}"})
    carrera = await carrera_repo.create({"codigo": f"CAR-{suffix}", "nombre": f"Carrera {suffix}"})
    cohorte = await cohorte_repo.create({"carrera_id": carrera.id, "nombre": f"2026-{suffix}"})
    return materia, carrera, cohorte


# ── 3.1 RED / 3.2 GREEN: mis_equipos ─────────────────────────────────────


async def test_mis_equipos_uses_current_user_identity_and_derives_estado_vigencia(
    db_session: AsyncSession, test_tenant, plain_user
):
    usuario = await make_usuario_perfil(db_session, test_tenant.id, plain_user.id)
    await _make_asignacion(
        db_session, test_tenant.id, usuario.id, "PROFESOR",
        desde=_HOY - datetime.timedelta(days=10),
    )

    current_user = CurrentUser(user_id=plain_user.id, tenant_id=test_tenant.id, roles=[])
    service = _make_service(db_session, test_tenant.id)

    result = await service.mis_equipos(current_user, filtros=None)

    assert len(result) == 1
    assert result[0].estado_vigencia == "Vigente"
    assert result[0].usuario_id == usuario.id


async def test_mis_equipos_does_not_return_other_users_asignaciones(
    db_session: AsyncSession, test_tenant, plain_user, admin_user
):
    usuario_a = await make_usuario_perfil(db_session, test_tenant.id, plain_user.id, "A", "A")
    usuario_b = await make_usuario_perfil(db_session, test_tenant.id, admin_user.id, "B", "B")
    await _make_asignacion(
        db_session, test_tenant.id, usuario_b.id, "PROFESOR",
        desde=_HOY - datetime.timedelta(days=10),
    )

    current_user = CurrentUser(user_id=plain_user.id, tenant_id=test_tenant.id, roles=[])
    service = _make_service(db_session, test_tenant.id)

    result = await service.mis_equipos(current_user, filtros=None)

    assert result == []


# ── 3.3 RED+GREEN+TRIANGULATE: asignacion_masiva ─────────────────────────


async def test_asignacion_masiva_creates_one_asignacion_per_usuario_and_audits(
    db_session: AsyncSession, test_tenant, plain_user, admin_user
):
    usuario_a = await make_usuario_perfil(db_session, test_tenant.id, plain_user.id, "A", "A")
    usuario_b = await make_usuario_perfil(db_session, test_tenant.id, admin_user.id, "B", "B")
    materia, carrera, cohorte = await _make_academic_context(db_session, test_tenant.id, "M1")

    current_user = CurrentUser(user_id=admin_user.id, tenant_id=test_tenant.id, roles=["ADMIN"])
    service = _make_service(db_session, test_tenant.id)

    data = AsignacionMasivaCreate(
        usuario_ids=[usuario_a.id, usuario_b.id],
        materia_id=materia.id,
        carrera_id=carrera.id,
        cohorte_id=cohorte.id,
        rol="PROFESOR",
        desde=_HOY,
    )

    resultado = await service.asignacion_masiva(data, current_user=current_user, request=_make_request())

    assert len(resultado.creadas) == 2
    assert resultado.ya_existentes == []
    assert resultado.filas_afectadas == 2

    audit_repo = AuditLogRepository(session=db_session, tenant_id=test_tenant.id)
    logs = await audit_repo.find_by(accion=AccionAuditoria.ASIGNACION_MODIFICAR)
    assert len(logs) == 1
    assert logs[0].filas_afectadas == 2


async def test_asignacion_masiva_omits_already_assigned_docente(
    db_session: AsyncSession, test_tenant, plain_user, admin_user
):
    usuario_a = await make_usuario_perfil(db_session, test_tenant.id, plain_user.id, "A", "A")
    usuario_b = await make_usuario_perfil(db_session, test_tenant.id, admin_user.id, "B", "B")
    materia, carrera, cohorte = await _make_academic_context(db_session, test_tenant.id, "M2")

    # usuario_a already has a Vigente PROFESOR asignacion in this context.
    await _make_asignacion(
        db_session, test_tenant.id, usuario_a.id, "PROFESOR",
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
        desde=_HOY - datetime.timedelta(days=10),
    )

    current_user = CurrentUser(user_id=admin_user.id, tenant_id=test_tenant.id, roles=["ADMIN"])
    service = _make_service(db_session, test_tenant.id)

    data = AsignacionMasivaCreate(
        usuario_ids=[usuario_a.id, usuario_b.id],
        materia_id=materia.id,
        carrera_id=carrera.id,
        cohorte_id=cohorte.id,
        rol="PROFESOR",
        desde=_HOY,
    )

    resultado = await service.asignacion_masiva(data, current_user=current_user, request=_make_request())

    assert resultado.creadas == [usuario_b.id]
    assert resultado.ya_existentes == [usuario_a.id]
    assert resultado.filas_afectadas == 1


async def test_asignacion_masiva_with_cross_tenant_usuario_raises_not_found(
    db_session: AsyncSession, test_tenant, another_tenant, admin_user, another_tenant_admin
):
    usuario_other_tenant = await make_usuario_perfil(db_session, another_tenant.id, another_tenant_admin.id, "X", "X")
    materia, carrera, cohorte = await _make_academic_context(db_session, test_tenant.id, "M3")

    current_user = CurrentUser(user_id=admin_user.id, tenant_id=test_tenant.id, roles=["ADMIN"])
    service = _make_service(db_session, test_tenant.id)

    data = AsignacionMasivaCreate(
        usuario_ids=[usuario_other_tenant.id],
        materia_id=materia.id,
        carrera_id=carrera.id,
        cohorte_id=cohorte.id,
        rol="PROFESOR",
        desde=_HOY,
    )

    try:
        await service.asignacion_masiva(data, current_user=current_user, request=_make_request())
        assert False, "expected NotFoundException"
    except NotFoundException:
        pass

    # No asignacion was created, no audit log emitted (abort total, D6).
    rows = await AsignacionRepository(session=db_session, tenant_id=test_tenant.id).find_by_filtros(test_tenant.id, filtros={})
    assert rows == []
    audit_repo = AuditLogRepository(session=db_session, tenant_id=test_tenant.id)
    logs = await audit_repo.find_by(accion=AccionAuditoria.ASIGNACION_MODIFICAR)
    assert logs == []


# ── 3.4 RED+GREEN+TRIANGULATE: clonar_equipo (RN-12) ─────────────────────


async def test_clonar_equipo_clones_vigentes_to_destino_with_new_dates(
    db_session: AsyncSession, test_tenant, plain_user, admin_user
):
    from app.models.cohorte import Cohorte

    usuario_a = await make_usuario_perfil(db_session, test_tenant.id, plain_user.id, "A", "A")
    usuario_b = await make_usuario_perfil(db_session, test_tenant.id, admin_user.id, "B", "B")
    materia, carrera, cohorte_origen = await _make_academic_context(db_session, test_tenant.id, "CL1")

    cohorte_repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=test_tenant.id)
    cohorte_destino = await cohorte_repo.create({"carrera_id": carrera.id, "nombre": "2026-CL1-DEST"})

    await _make_asignacion(
        db_session, test_tenant.id, usuario_a.id, "PROFESOR",
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte_origen.id,
        desde=_HOY - datetime.timedelta(days=10),
        comisiones=["A", "B"],
    )
    await _make_asignacion(
        db_session, test_tenant.id, usuario_b.id, "TUTOR",
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte_origen.id,
        desde=_HOY - datetime.timedelta(days=10),
        responsable_id=usuario_a.id,
    )

    current_user = CurrentUser(user_id=admin_user.id, tenant_id=test_tenant.id, roles=["ADMIN"])
    service = _make_service(db_session, test_tenant.id)

    nueva_desde = _HOY
    nueva_hasta = _HOY + datetime.timedelta(days=180)

    data = ClonarEquipoCreate(
        materia_id=materia.id,
        carrera_id=carrera.id,
        cohorte_origen_id=cohorte_origen.id,
        cohorte_destino_id=cohorte_destino.id,
        desde=nueva_desde,
        hasta=nueva_hasta,
    )

    resultado = await service.clonar_equipo(data, current_user=current_user, request=_make_request())

    assert resultado.filas_afectadas == 2
    assert len(resultado.creadas) == 2

    destino_rows = await AsignacionRepository(session=db_session, tenant_id=test_tenant.id).find_equipo(
        test_tenant.id, materia.id, carrera.id, cohorte_destino.id
    )
    assert len(destino_rows) == 2
    by_usuario = {row.usuario_id: row for row in destino_rows}

    cloned_a = by_usuario[usuario_a.id]
    assert cloned_a.rol == "PROFESOR"
    assert cloned_a.comisiones == ["A", "B"]
    assert cloned_a.desde == nueva_desde
    assert cloned_a.hasta == nueva_hasta

    cloned_b = by_usuario[usuario_b.id]
    assert cloned_b.rol == "TUTOR"
    assert cloned_b.responsable_id == usuario_a.id

    audit_repo = AuditLogRepository(session=db_session, tenant_id=test_tenant.id)
    logs = await audit_repo.find_by(accion=AccionAuditoria.ASIGNACION_MODIFICAR)
    assert len(logs) == 1
    assert logs[0].filas_afectadas == 2


async def test_clonar_equipo_excludes_vencidas(
    db_session: AsyncSession, test_tenant, plain_user, admin_user
):
    from app.models.cohorte import Cohorte

    usuario_a = await make_usuario_perfil(db_session, test_tenant.id, plain_user.id, "A", "A")
    usuario_b = await make_usuario_perfil(db_session, test_tenant.id, admin_user.id, "B", "B")
    materia, carrera, cohorte_origen = await _make_academic_context(db_session, test_tenant.id, "CL2")

    cohorte_repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=test_tenant.id)
    cohorte_destino = await cohorte_repo.create({"carrera_id": carrera.id, "nombre": "2026-CL2-DEST"})

    # Vigente.
    await _make_asignacion(
        db_session, test_tenant.id, usuario_a.id, "PROFESOR",
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte_origen.id,
        desde=_HOY - datetime.timedelta(days=10),
    )
    # Vencida.
    await _make_asignacion(
        db_session, test_tenant.id, usuario_b.id, "TUTOR",
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte_origen.id,
        desde=_HOY - datetime.timedelta(days=60),
        hasta=_HOY - datetime.timedelta(days=1),
    )

    current_user = CurrentUser(user_id=admin_user.id, tenant_id=test_tenant.id, roles=["ADMIN"])
    service = _make_service(db_session, test_tenant.id)

    data = ClonarEquipoCreate(
        materia_id=materia.id,
        carrera_id=carrera.id,
        cohorte_origen_id=cohorte_origen.id,
        cohorte_destino_id=cohorte_destino.id,
        desde=_HOY,
    )

    resultado = await service.clonar_equipo(data, current_user=current_user, request=_make_request())

    assert resultado.filas_afectadas == 1
    destino_rows = await AsignacionRepository(session=db_session, tenant_id=test_tenant.id).find_equipo(
        test_tenant.id, materia.id, carrera.id, cohorte_destino.id
    )
    assert len(destino_rows) == 1
    assert destino_rows[0].usuario_id == usuario_a.id


async def test_clonar_equipo_does_not_duplicate_existing_equivalent_in_destino(
    db_session: AsyncSession, test_tenant, plain_user, admin_user
):
    from app.models.cohorte import Cohorte

    usuario_a = await make_usuario_perfil(db_session, test_tenant.id, plain_user.id, "A", "A")
    materia, carrera, cohorte_origen = await _make_academic_context(db_session, test_tenant.id, "CL3")

    cohorte_repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=test_tenant.id)
    cohorte_destino = await cohorte_repo.create({"carrera_id": carrera.id, "nombre": "2026-CL3-DEST"})

    await _make_asignacion(
        db_session, test_tenant.id, usuario_a.id, "PROFESOR",
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte_origen.id,
        desde=_HOY - datetime.timedelta(days=10),
    )
    # Equivalent already present in destino.
    await _make_asignacion(
        db_session, test_tenant.id, usuario_a.id, "PROFESOR",
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte_destino.id,
        desde=_HOY,
    )

    current_user = CurrentUser(user_id=admin_user.id, tenant_id=test_tenant.id, roles=["ADMIN"])
    service = _make_service(db_session, test_tenant.id)

    data = ClonarEquipoCreate(
        materia_id=materia.id,
        carrera_id=carrera.id,
        cohorte_origen_id=cohorte_origen.id,
        cohorte_destino_id=cohorte_destino.id,
        desde=_HOY,
    )

    resultado = await service.clonar_equipo(data, current_user=current_user, request=_make_request())

    assert resultado.creadas == []
    assert resultado.ya_existentes == [usuario_a.id]
    assert resultado.filas_afectadas == 0

    destino_rows = await AsignacionRepository(session=db_session, tenant_id=test_tenant.id).find_equipo(
        test_tenant.id, materia.id, carrera.id, cohorte_destino.id
    )
    assert len(destino_rows) == 1


async def test_clonar_equipo_cross_tenant_cohorte_raises_not_found(
    db_session: AsyncSession, test_tenant, another_tenant, plain_user, admin_user, another_tenant_admin
):
    from app.models.cohorte import Cohorte

    usuario_a = await make_usuario_perfil(db_session, test_tenant.id, plain_user.id, "A", "A")
    materia, carrera, cohorte_origen = await _make_academic_context(db_session, test_tenant.id, "CL4")

    await _make_asignacion(
        db_session, test_tenant.id, usuario_a.id, "PROFESOR",
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte_origen.id,
        desde=_HOY - datetime.timedelta(days=10),
    )

    # cohorte_destino belongs to another_tenant.
    other_cohorte_repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=another_tenant.id)
    cohorte_destino_otro = await other_cohorte_repo.create({"carrera_id": carrera.id, "nombre": "OTRO-DEST"})

    current_user = CurrentUser(user_id=admin_user.id, tenant_id=test_tenant.id, roles=["ADMIN"])
    service = _make_service(db_session, test_tenant.id)

    data = ClonarEquipoCreate(
        materia_id=materia.id,
        carrera_id=carrera.id,
        cohorte_origen_id=cohorte_origen.id,
        cohorte_destino_id=cohorte_destino_otro.id,
        desde=_HOY,
    )

    try:
        await service.clonar_equipo(data, current_user=current_user, request=_make_request())
        assert False, "expected NotFoundException"
    except NotFoundException:
        pass

    audit_repo = AuditLogRepository(session=db_session, tenant_id=test_tenant.id)
    logs = await audit_repo.find_by(accion=AccionAuditoria.ASIGNACION_MODIFICAR)
    assert logs == []


# ── 3.5 RED+GREEN+TRIANGULATE: modificar_vigencia ────────────────────────


async def test_modificar_vigencia_updates_equipo_and_audits(
    db_session: AsyncSession, test_tenant, plain_user, admin_user
):
    usuario_a = await make_usuario_perfil(db_session, test_tenant.id, plain_user.id, "A", "A")
    usuario_b = await make_usuario_perfil(db_session, test_tenant.id, admin_user.id, "B", "B")
    materia, carrera, cohorte = await _make_academic_context(db_session, test_tenant.id, "V1")

    await _make_asignacion(
        db_session, test_tenant.id, usuario_a.id, "PROFESOR",
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
        desde=_HOY - datetime.timedelta(days=100),
    )
    await _make_asignacion(
        db_session, test_tenant.id, usuario_b.id, "TUTOR",
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
        desde=_HOY - datetime.timedelta(days=100),
    )

    current_user = CurrentUser(user_id=admin_user.id, tenant_id=test_tenant.id, roles=["ADMIN"])
    service = _make_service(db_session, test_tenant.id)

    nueva_hasta = _HOY + datetime.timedelta(days=365)
    data = VigenciaEquipoUpdate(
        materia_id=materia.id,
        carrera_id=carrera.id,
        cohorte_id=cohorte.id,
        hasta=nueva_hasta,
    )

    filas_afectadas = await service.modificar_vigencia(data, current_user=current_user, request=_make_request())

    assert filas_afectadas == 2

    rows = await AsignacionRepository(session=db_session, tenant_id=test_tenant.id).find_equipo(
        test_tenant.id, materia.id, carrera.id, cohorte.id
    )
    for row in rows:
        assert row.hasta == nueva_hasta

    audit_repo = AuditLogRepository(session=db_session, tenant_id=test_tenant.id)
    logs = await audit_repo.find_by(accion=AccionAuditoria.ASIGNACION_MODIFICAR)
    assert len(logs) == 1
    assert logs[0].filas_afectadas == 2


async def test_modificar_vigencia_empty_equipo_returns_zero_without_error(
    db_session: AsyncSession, test_tenant, admin_user
):
    materia, carrera, cohorte = await _make_academic_context(db_session, test_tenant.id, "V2")

    current_user = CurrentUser(user_id=admin_user.id, tenant_id=test_tenant.id, roles=["ADMIN"])
    service = _make_service(db_session, test_tenant.id)

    data = VigenciaEquipoUpdate(
        materia_id=materia.id,
        carrera_id=carrera.id,
        cohorte_id=cohorte.id,
        desde=_HOY,
    )

    filas_afectadas = await service.modificar_vigencia(data, current_user=current_user, request=_make_request())

    assert filas_afectadas == 0

    audit_repo = AuditLogRepository(session=db_session, tenant_id=test_tenant.id)
    logs = await audit_repo.find_by(accion=AccionAuditoria.ASIGNACION_MODIFICAR)
    assert len(logs) == 1
    assert logs[0].filas_afectadas == 0


# ── 3.6 RED+GREEN+TRIANGULATE: exportar_equipo ───────────────────────────


async def test_exportar_equipo_returns_csv_rows_for_each_asignacion(
    db_session: AsyncSession, test_tenant, plain_user, admin_user
):
    usuario_a = await make_usuario_perfil(db_session, test_tenant.id, plain_user.id, "Ana", "Perez")
    usuario_b = await make_usuario_perfil(db_session, test_tenant.id, admin_user.id, "Beto", "Gomez")
    materia, carrera, cohorte = await _make_academic_context(db_session, test_tenant.id, "EX1")

    await _make_asignacion(
        db_session, test_tenant.id, usuario_a.id, "PROFESOR",
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
        desde=_HOY - datetime.timedelta(days=10),
    )
    await _make_asignacion(
        db_session, test_tenant.id, usuario_b.id, "TUTOR",
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
        desde=_HOY - datetime.timedelta(days=60),
        hasta=_HOY - datetime.timedelta(days=1),  # vencida
    )

    current_user = CurrentUser(user_id=admin_user.id, tenant_id=test_tenant.id, roles=["ADMIN"])
    service = _make_service(db_session, test_tenant.id)

    items = await service.exportar_equipo(
        {"materia_id": materia.id, "carrera_id": carrera.id, "cohorte_id": cohorte.id},
        current_user=current_user,
    )

    assert len(items) == 2
    by_docente = {item.docente: item for item in items}
    assert "Ana Perez" in by_docente
    assert by_docente["Ana Perez"].estado_vigencia == "Vigente"
    assert "Beto Gomez" in by_docente
    assert by_docente["Beto Gomez"].estado_vigencia == "Vencida"

    # Read-only operation: no ASIGNACION_MODIFICAR audit entry.
    audit_repo = AuditLogRepository(session=db_session, tenant_id=test_tenant.id)
    logs = await audit_repo.find_by(accion=AccionAuditoria.ASIGNACION_MODIFICAR)
    assert logs == []


async def test_exportar_equipo_other_tenant_raises_not_found(
    db_session: AsyncSession, test_tenant, another_tenant, plain_user, admin_user
):
    usuario = await make_usuario_perfil(db_session, test_tenant.id, plain_user.id)
    materia, carrera, cohorte = await _make_academic_context(db_session, test_tenant.id, "EX2")

    await _make_asignacion(
        db_session, test_tenant.id, usuario.id, "PROFESOR",
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
        desde=_HOY - datetime.timedelta(days=10),
    )

    # A caller from another_tenant requesting the same context ids: the
    # materia/carrera/cohorte belong to test_tenant, not another_tenant, so
    # they are indistinguishable from "no existe" (D4 [SEC], regla dura #9).
    current_user = CurrentUser(user_id=admin_user.id, tenant_id=another_tenant.id, roles=["ADMIN"])
    service = _make_service(db_session, another_tenant.id)

    try:
        await service.exportar_equipo(
            {"materia_id": materia.id, "carrera_id": carrera.id, "cohorte_id": cohorte.id},
            current_user=current_user,
        )
        assert False, "expected NotFoundException"
    except NotFoundException:
        pass


# ── Group 4 wiring: listar_equipos / buscar_docentes passthroughs ───────


async def test_listar_equipos_returns_tenant_scoped_rows(
    db_session: AsyncSession, test_tenant, another_tenant, plain_user, admin_user, another_tenant_admin
):
    usuario_a = await make_usuario_perfil(db_session, test_tenant.id, plain_user.id, "A", "A")
    materia, carrera, cohorte = await _make_academic_context(db_session, test_tenant.id, "LST1")
    await _make_asignacion(
        db_session, test_tenant.id, usuario_a.id, "PROFESOR",
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
        desde=_HOY - datetime.timedelta(days=10),
    )

    # Row in another tenant must not leak into the listado.
    usuario_other = await make_usuario_perfil(db_session, another_tenant.id, another_tenant_admin.id, "X", "X")
    await _make_asignacion(
        db_session, another_tenant.id, usuario_other.id, "PROFESOR",
        desde=_HOY - datetime.timedelta(days=10),
    )

    service = _make_service(db_session, test_tenant.id)

    rows = await service.listar_equipos(test_tenant.id, filtros=None)

    assert len(rows) == 1
    assert rows[0].usuario_id == usuario_a.id


async def test_buscar_docentes_matches_partial_name_scoped_to_tenant(
    db_session: AsyncSession, test_tenant, another_tenant, plain_user, another_tenant_admin
):
    await make_usuario_perfil(db_session, test_tenant.id, plain_user.id, "Ana", "Perez")
    await make_usuario_perfil(db_session, another_tenant.id, another_tenant_admin.id, "Anabel", "Gomez")

    service = _make_service(db_session, test_tenant.id)

    result = await service.buscar_docentes(test_tenant.id, "Ana")

    assert len(result) == 1
    assert result[0].nombre == "Ana"
