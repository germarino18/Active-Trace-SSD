"""Tests for Aviso and AcknowledgmentAviso models."""

from datetime import UTC, datetime
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.aviso import Aviso, AcknowledgmentAviso, AlcanceAviso, SeveridadAviso
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.models.user import User
from app.repositories.base import BaseRepository


_JAN2026 = datetime(2026, 1, 1, tzinfo=UTC)
_DEC2026 = datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC)


@pytest.fixture
async def test_usuario(db_session: AsyncSession, test_tenant: Tenant) -> Usuario:
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    user = await user_repo.create({
        "email": f"usr-{uuid.uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "Usuario Test",
    })
    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    return await usuario_repo.create({
        "user_id": user.id,
        "nombre": "Test",
        "apellidos": "Usuario",
    })


@pytest.mark.asyncio
async def test_create_aviso_global(db_session: AsyncSession, test_tenant: Tenant):
    repo = BaseRepository(model=Aviso, session=db_session, tenant_id=test_tenant.id)
    aviso = await repo.create({
        "alcance": AlcanceAviso.GLOBAL.value,
        "severidad": SeveridadAviso.INFO.value,
        "titulo": "Aviso importante",
        "cuerpo": "Este es un aviso de prueba",
        "inicio_en": _JAN2026,
        "fin_en": _DEC2026,
        "orden": 1,
        "activo": True,
        "requiere_ack": False,
    })
    assert aviso.id is not None
    assert aviso.tenant_id == test_tenant.id
    assert aviso.alcance == AlcanceAviso.GLOBAL.value
    assert aviso.severidad == SeveridadAviso.INFO.value
    assert aviso.titulo == "Aviso importante"
    assert aviso.activo is True
    assert aviso.requiere_ack is False
    assert aviso.deleted_at is None


@pytest.mark.asyncio
async def test_create_aviso_with_all_fields(db_session: AsyncSession, test_tenant: Tenant):
    repo = BaseRepository(model=Aviso, session=db_session, tenant_id=test_tenant.id)
    aviso = await repo.create({
        "alcance": AlcanceAviso.POR_ROL.value,
        "severidad": SeveridadAviso.CRITICO.value,
        "titulo": "Critico",
        "cuerpo": "Mensaje critico",
        "rol_destino": "ALUMNO",
        "inicio_en": datetime(2026, 6, 1, tzinfo=UTC),
        "fin_en": datetime(2026, 6, 30, 23, 59, 59, tzinfo=UTC),
        "orden": 10,
        "activo": True,
        "requiere_ack": True,
    })
    assert aviso.id is not None
    assert aviso.rol_destino == "ALUMNO"
    assert aviso.severidad == SeveridadAviso.CRITICO.value
    assert aviso.orden == 10
    assert aviso.requiere_ack is True


@pytest.mark.asyncio
async def test_create_acknowledgment(
    db_session: AsyncSession,
    test_tenant: Tenant,
    test_usuario: Usuario,
):
    aviso_repo = BaseRepository(model=Aviso, session=db_session, tenant_id=test_tenant.id)
    aviso = await aviso_repo.create({
        "alcance": AlcanceAviso.GLOBAL.value,
        "severidad": SeveridadAviso.INFO.value,
        "titulo": "Ack test",
        "cuerpo": "Cuerpo",
        "inicio_en": _JAN2026,
        "fin_en": _DEC2026,
        "requiere_ack": True,
    })
    ack_repo = BaseRepository(
        model=AcknowledgmentAviso,
        session=db_session,
        tenant_id=test_tenant.id,
    )
    ack = await ack_repo.create({
        "aviso_id": aviso.id,
        "usuario_id": test_usuario.id,
    })
    assert ack.id is not None
    assert ack.aviso_id == aviso.id
    assert ack.usuario_id == test_usuario.id
    assert ack.confirmado_at is not None


@pytest.mark.asyncio
async def test_soft_delete_aviso(db_session: AsyncSession, test_tenant: Tenant):
    repo = BaseRepository(model=Aviso, session=db_session, tenant_id=test_tenant.id)
    aviso = await repo.create({
        "alcance": AlcanceAviso.GLOBAL.value,
        "severidad": SeveridadAviso.INFO.value,
        "titulo": "To delete",
        "cuerpo": "Sera borrado",
        "inicio_en": _JAN2026,
        "fin_en": _DEC2026,
    })
    assert aviso.deleted_at is None
    deleted = await repo.soft_delete(aviso.id)
    assert deleted.deleted_at is not None
    not_found = await repo.find_by_id(aviso.id)
    assert not_found is None


@pytest.mark.asyncio
async def test_multi_tenant_isolation(db_session: AsyncSession, test_tenant: Tenant, another_tenant: Tenant):
    repo1 = BaseRepository(model=Aviso, session=db_session, tenant_id=test_tenant.id)
    repo2 = BaseRepository(model=Aviso, session=db_session, tenant_id=another_tenant.id)
    await repo1.create({
        "alcance": AlcanceAviso.GLOBAL.value,
        "severidad": SeveridadAviso.INFO.value,
        "titulo": "T1",
        "cuerpo": "Tenant 1",
        "inicio_en": _JAN2026,
        "fin_en": _DEC2026,
    })
    await repo2.create({
        "alcance": AlcanceAviso.GLOBAL.value,
        "severidad": SeveridadAviso.INFO.value,
        "titulo": "T2",
        "cuerpo": "Tenant 2",
        "inicio_en": _JAN2026,
        "fin_en": _DEC2026,
    })
    t1_all = await repo1.find_all()
    t2_all = await repo2.find_all()
    assert len(t1_all) == 1
    assert len(t2_all) == 1
    assert t1_all[0].titulo == "T1"
    assert t2_all[0].titulo == "T2"
