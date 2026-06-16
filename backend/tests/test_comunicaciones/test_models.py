"""Tests for the Comunicacion model."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comunicacion import Comunicacion, ComunicacionEstado
from app.models.materia import Materia
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.repositories.base import BaseRepository


@pytest.fixture
async def test_materia(db_session: AsyncSession, test_tenant: Tenant) -> Materia:
    repo = BaseRepository(model=Materia, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({"codigo": "MAT-COM", "nombre": "Comunicaciones Test"})


@pytest.fixture
async def test_usuario(db_session: AsyncSession, test_tenant: Tenant) -> Usuario:
    repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    # Usuario needs a user_id; we create a dummy one
    from app.models.user import User
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    user = await user_repo.create({
            "email": f"prof-{uuid.uuid4().hex[:8]}@test.com",
            "password_hash": "dummy_hash",
            "display_name": "Profesor Test",
        })
    return await repo.create({"user_id": user.id, "nombre": "Profesor", "apellidos": "Test"})


@pytest.mark.asyncio
async def test_create_comunicacion(
    db_session: AsyncSession,
    test_tenant: Tenant,
    test_materia: Materia,
    test_usuario: Usuario,
):
    """Test creating a Comunicacion with required fields."""
    repo = BaseRepository(model=Comunicacion, session=db_session, tenant_id=test_tenant.id)
    com = await repo.create(
        {
            "enviado_por": test_usuario.id,
            "materia_id": test_materia.id,
            "destinatario": "alumno@test.com",
            "destinatario_hash": "abc123",
            "asunto": "Notificación de atraso",
            "cuerpo": "Estimado alumno, tiene actividades pendientes.",
            "lote_id": uuid.uuid4(),
        }
    )
    assert com.id is not None
    assert com.tenant_id == test_tenant.id
    assert com.estado == ComunicacionEstado.PENDIENTE
    assert com.destinatario == "alumno@test.com"
    assert com.asunto == "Notificación de atraso"
    assert com.enviado_at is None
    assert com.reintentos == 0


@pytest.mark.asyncio
async def test_create_comunicacion_sets_default_estado(
    db_session: AsyncSession,
    test_tenant: Tenant,
    test_materia: Materia,
    test_usuario: Usuario,
):
    """Verify estado defaults to Pendiente when not specified."""
    repo = BaseRepository(model=Comunicacion, session=db_session, tenant_id=test_tenant.id)
    com = await repo.create(
        {
            "enviado_por": test_usuario.id,
            "materia_id": test_materia.id,
            "destinatario": "otro@test.com",
            "destinatario_hash": "def456",
            "asunto": "Test",
            "cuerpo": "Cuerpo",
            "lote_id": uuid.uuid4(),
        }
    )
    assert com.estado == ComunicacionEstado.PENDIENTE


@pytest.mark.asyncio
async def test_comunicacion_multi_tenant_isolation(
    db_session: AsyncSession,
    test_tenant: Tenant,
    another_tenant: Tenant,
    test_materia: Materia,
    test_usuario: Usuario,
):
    """Verify comunicaciones from different tenants are isolated."""
    # Create a materia and usuario in another_tenant
    from app.models.user import User

    otro_materia_repo = BaseRepository(model=Materia, session=db_session, tenant_id=another_tenant.id)
    otro_materia = await otro_materia_repo.create({"codigo": "MAT-OTRO", "nombre": "Otra Materia"})

    otro_user_repo = BaseRepository(model=User, session=db_session, tenant_id=another_tenant.id)
    otro_user = await otro_user_repo.create({
        "email": f"otro-{uuid.uuid4().hex[:8]}@test.com",
        "password_hash": "dummy_hash",
        "display_name": "Otro Profesor",
    })
    otro_usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=another_tenant.id)
    otro_usuario = await otro_usuario_repo.create({"user_id": otro_user.id, "nombre": "Otro", "apellidos": "Profesor"})

    repo1 = BaseRepository(model=Comunicacion, session=db_session, tenant_id=test_tenant.id)
    repo2 = BaseRepository(model=Comunicacion, session=db_session, tenant_id=another_tenant.id)

    lote = uuid.uuid4()
    await repo1.create(
        {
            "enviado_por": test_usuario.id,
            "materia_id": test_materia.id,
            "destinatario": "t1@test.com",
            "destinatario_hash": "hash1",
            "asunto": "T1",
            "cuerpo": "Cuerpo T1",
            "lote_id": lote,
        }
    )
    await repo2.create(
        {
            "enviado_por": otro_usuario.id,
            "materia_id": otro_materia.id,
            "destinatario": "t2@test.com",
            "destinatario_hash": "hash2",
            "asunto": "T2",
            "cuerpo": "Cuerpo T2",
            "lote_id": lote,
        }
    )

    t1_items = await repo1.find_all()
    t2_items = await repo2.find_all()

    assert len(t1_items) == 1
    assert len(t2_items) == 1
    assert t1_items[0].destinatario == "t1@test.com"
    assert t2_items[0].destinatario == "t2@test.com"
