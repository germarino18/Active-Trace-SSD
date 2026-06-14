"""Model tests for `Usuario` (C-07 task group 2).

`Usuario` is the business profile, 1:1 with the auth identity `users` via
`user_id` (FK -> users.id, UNIQUE). It carries PII (`dni`, `cuil`, `cbu`,
`alias_cbu`) encrypted at rest via `EncryptedString`, plus business
attributes (`legajo`, `legajo_profesional`, `facturador`, `banco`,
`regional`, `estado`). It uses BaseMixin + TenantMixin + SoftDeleteMixin +
AuditMixin and has NO `email` column (D1 — email lives only on `users`).
"""

import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.usuario import Usuario
from app.repositories.base import BaseRepository
from app.services.auth.password_service import PasswordService


async def _make_user(db_session: AsyncSession, tenant_id, email="profile@example.com"):
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
    return user


# ── 2.1 RED: shape of Usuario ────────────────────────────────────────────


async def test_usuario_persists_with_expected_columns(db_session: AsyncSession, test_tenant):
    user = await _make_user(db_session, test_tenant.id)
    repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)

    usuario = await repo.create(
        {
            "user_id": user.id,
            "nombre": "Ada",
            "apellidos": "Lovelace",
            "dni": "12345678",
            "cuil": "27-12345678-3",
            "cbu": "0000003100012345678901",
            "alias_cbu": "ADA.LOVELACE.MP",
            "banco": "Banco Nación",
            "regional": "CABA",
            "legajo": "L-001",
            "legajo_profesional": "MP-9876",
            "facturador": True,
            "estado": "Activo",
        }
    )

    assert usuario.id is not None
    assert usuario.tenant_id == test_tenant.id
    assert usuario.user_id == user.id
    assert usuario.nombre == "Ada"
    assert usuario.apellidos == "Lovelace"
    assert usuario.dni == "12345678"
    assert usuario.cuil == "27-12345678-3"
    assert usuario.cbu == "0000003100012345678901"
    assert usuario.alias_cbu == "ADA.LOVELACE.MP"
    assert usuario.banco == "Banco Nación"
    assert usuario.regional == "CABA"
    assert usuario.legajo == "L-001"
    assert usuario.legajo_profesional == "MP-9876"
    assert usuario.facturador is True
    assert usuario.estado == "Activo"
    assert usuario.deleted_at is None
    assert not hasattr(Usuario, "email")


async def test_usuario_estado_defaults_to_activo(db_session: AsyncSession, test_tenant):
    user = await _make_user(db_session, test_tenant.id, email="default-estado@example.com")
    repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)

    usuario = await repo.create({"user_id": user.id, "nombre": "Grace", "apellidos": "Hopper"})

    assert usuario.estado == "Activo"
    assert usuario.facturador is False


# ── 2.3 TRIANGULATE: EncryptedString + unique (tenant_id, user_id) ───────


async def test_usuario_pii_is_ciphertext_at_rest(db_session: AsyncSession, test_tenant):
    user = await _make_user(db_session, test_tenant.id, email="pii@example.com")
    repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)

    usuario = await repo.create(
        {
            "user_id": user.id,
            "nombre": "Pii",
            "apellidos": "Test",
            "dni": "30222333",
            "cuil": "20-30222333-4",
            "cbu": "1111122223333344445555",
            "alias_cbu": "pii.test.mp",
        }
    )
    await db_session.flush()

    raw = await db_session.execute(
        text("SELECT dni, cuil, cbu, alias_cbu FROM usuario WHERE id = :id"),
        {"id": usuario.id},
    )
    row = raw.one()

    assert row.dni != "30222333"
    assert row.cuil != "20-30222333-4"
    assert row.cbu != "1111122223333344445555"
    assert row.alias_cbu != "pii.test.mp"

    # ORM read returns plaintext.
    await db_session.refresh(usuario)
    assert usuario.dni == "30222333"
    assert usuario.cuil == "20-30222333-4"
    assert usuario.cbu == "1111122223333344445555"
    assert usuario.alias_cbu == "pii.test.mp"


async def test_usuario_user_id_unique_among_alive_rows(db_session: AsyncSession, test_tenant):
    user = await _make_user(db_session, test_tenant.id, email="dup@example.com")
    repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)

    await repo.create({"user_id": user.id, "nombre": "Primero", "apellidos": "Uno"})

    with pytest.raises(IntegrityError):
        await repo.create({"user_id": user.id, "nombre": "Segundo", "apellidos": "Dos"})
        await db_session.flush()


async def test_usuario_user_id_can_be_reused_after_soft_delete(
    db_session: AsyncSession, test_tenant
):
    user = await _make_user(db_session, test_tenant.id, email="resoftdelete@example.com")
    repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)

    first = await repo.create({"user_id": user.id, "nombre": "Primero", "apellidos": "Uno"})
    await repo.soft_delete(first.id)

    recreated = await repo.create({"user_id": user.id, "nombre": "Segundo", "apellidos": "Dos"})

    assert recreated.id != first.id
    assert recreated.user_id == user.id
