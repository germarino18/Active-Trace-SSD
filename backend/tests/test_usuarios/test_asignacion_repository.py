"""Tests for `AsignacionRepository.find_roles_vigentes` (C-07 task group 5).

`estado_vigencia` is derived (D3), never stored: an asignacion is *Vigente*
iff `desde <= hoy AND (hasta IS NULL OR hoy <= hasta)`. `find_roles_vigentes`
returns the DISTINCT `rol` values of alive (`deleted_at IS NULL`), Vigente
asignaciones for a given `tenant_id` + `usuario_id`. This list feeds
`TokenService.create_access_token`'s `roles` claim (group 6).
"""

import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asignacion import Asignacion
from app.models.user import User
from app.models.usuario import Usuario
from app.repositories.asignacion_repository import AsignacionRepository
from app.repositories.base import BaseRepository
from app.services.auth.password_service import PasswordService

_HOY = datetime.date.today()


async def _make_usuario(db_session: AsyncSession, tenant_id, email):
    pw = PasswordService()
    user = User(
        tenant_id=tenant_id,
        email=email,
        password_hash=pw.hash_password("Password123!"),
        display_name=email,
        roles=[],
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=tenant_id)
    return await usuario_repo.create({"user_id": user.id, "nombre": "N", "apellidos": "A"})


async def _make_asignacion(db_session, tenant_id, usuario_id, rol, *, desde, hasta=None):
    repo = BaseRepository(model=Asignacion, session=db_session, tenant_id=tenant_id)
    return await repo.create(
        {
            "usuario_id": usuario_id,
            "rol": rol,
            "desde": desde,
            "hasta": hasta,
        }
    )


# ── 5.2 RED: happy path — a single vigente asignacion is returned ────────


async def test_find_roles_vigentes_returns_vigente_role(db_session: AsyncSession, test_tenant):
    usuario = await _make_usuario(db_session, test_tenant.id, "vigente@example.com")
    await _make_asignacion(
        db_session, test_tenant.id, usuario.id, "PROFESOR",
        desde=_HOY - datetime.timedelta(days=10),
    )

    repo = AsignacionRepository(session=db_session, tenant_id=test_tenant.id)
    roles = await repo.find_roles_vigentes(test_tenant.id, usuario.id)

    assert roles == {"PROFESOR"}


# ── 5.4 TRIANGULATE: Vencida excluded, future-dated excluded, multi-rol ──


async def test_find_roles_vigentes_excludes_vencida(db_session: AsyncSession, test_tenant):
    usuario = await _make_usuario(db_session, test_tenant.id, "vencida@example.com")
    # Vencida: hasta is in the past.
    await _make_asignacion(
        db_session, test_tenant.id, usuario.id, "TUTOR",
        desde=_HOY - datetime.timedelta(days=60),
        hasta=_HOY - datetime.timedelta(days=1),
    )

    repo = AsignacionRepository(session=db_session, tenant_id=test_tenant.id)
    roles = await repo.find_roles_vigentes(test_tenant.id, usuario.id)

    assert roles == set()


async def test_find_roles_vigentes_excludes_future_dated(db_session: AsyncSession, test_tenant):
    usuario = await _make_usuario(db_session, test_tenant.id, "futuro@example.com")
    # desde is in the future: not yet vigente.
    await _make_asignacion(
        db_session, test_tenant.id, usuario.id, "COORDINADOR",
        desde=_HOY + datetime.timedelta(days=5),
    )

    repo = AsignacionRepository(session=db_session, tenant_id=test_tenant.id)
    roles = await repo.find_roles_vigentes(test_tenant.id, usuario.id)

    assert roles == set()


async def test_find_roles_vigentes_returns_all_distinct_vigente_roles(
    db_session: AsyncSession, test_tenant
):
    usuario = await _make_usuario(db_session, test_tenant.id, "multirol@example.com")
    await _make_asignacion(
        db_session, test_tenant.id, usuario.id, "PROFESOR",
        desde=_HOY - datetime.timedelta(days=30),
    )
    await _make_asignacion(
        db_session, test_tenant.id, usuario.id, "TUTOR",
        desde=_HOY - datetime.timedelta(days=10), hasta=_HOY + datetime.timedelta(days=10),
    )
    # Vencida asignacion for the same role should not produce duplicates
    # or leak into the result either.
    await _make_asignacion(
        db_session, test_tenant.id, usuario.id, "COORDINADOR",
        desde=_HOY - datetime.timedelta(days=100),
        hasta=_HOY - datetime.timedelta(days=50),
    )

    repo = AsignacionRepository(session=db_session, tenant_id=test_tenant.id)
    roles = await repo.find_roles_vigentes(test_tenant.id, usuario.id)

    assert roles == {"PROFESOR", "TUTOR"}
