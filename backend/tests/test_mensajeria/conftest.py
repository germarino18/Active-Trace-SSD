"""Fixtures for mensajeria tests."""
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant
from app.models.user import User
from app.models.usuario import Usuario
from app.models.hilo_conversacion import HiloConversacion
from app.models.hilo_participante import HiloParticipante
from app.models.mensaje import Mensaje
from app.repositories.base import BaseRepository
from app.schemas.auth import CurrentUser
from tests.helpers import cleanup_permission_cache, seed_permissions_for_tenant


@pytest.fixture
async def auth_user_inbox(db_session, test_tenant) -> CurrentUser:
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    user = await user_repo.create({
        "email": f"inbox-user-{uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "Inbox User",
        "is_active": True,
    })
    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    await usuario_repo.create({
        "user_id": user.id,
        "nombre": "Inbox",
        "apellidos": "User",
    })
    return CurrentUser(
        user_id=user.id,
        tenant_id=test_tenant.id,
        roles=["PROFESOR"],
    )


@pytest.fixture
async def auth_usuario(db_session, test_tenant, auth_user_inbox: CurrentUser) -> Usuario:
    """Devuelve Usuario (perfil) del auth_user_inbox."""
    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    from sqlalchemy import select
    result = await db_session.execute(
        select(Usuario).where(Usuario.user_id == auth_user_inbox.user_id)
    )
    usuario = result.scalar_one()
    return usuario


@pytest.fixture
async def otro_usuario(db_session: AsyncSession, test_tenant: Tenant) -> Usuario:
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    user = await user_repo.create({
        "email": f"otro-{uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "Otro",
        "is_active": True,
    })
    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    return await usuario_repo.create({
        "user_id": user.id,
        "nombre": "Otro",
        "apellidos": "Usuario",
    })


@pytest.fixture
async def test_hilo(db_session: AsyncSession, test_tenant: Tenant, auth_usuario: Usuario, otro_usuario: Usuario) -> HiloConversacion:
    """Hilo entre auth_user_inbox y otro_usuario con un mensaje."""
    hilo_repo = BaseRepository(model=HiloConversacion, session=db_session, tenant_id=test_tenant.id)
    hilo = await hilo_repo.create({"asunto": "Test conversation"})

    # Add participants
    participante_repo = BaseRepository(model=HiloParticipante, session=db_session, tenant_id=test_tenant.id)
    await participante_repo.create({
        "hilo_id": hilo.id,
        "usuario_id": auth_usuario.id,
    })
    await participante_repo.create({
        "hilo_id": hilo.id,
        "usuario_id": otro_usuario.id,
    })

    # Add first message from otro_usuario
    mensaje_repo = BaseRepository(model=Mensaje, session=db_session, tenant_id=test_tenant.id)
    await mensaje_repo.create({
        "hilo_id": hilo.id,
        "remitente_id": otro_usuario.id,
        "contenido": "Hola, este es un mensaje de prueba",
        "created_at": datetime.now(timezone.utc),
    })

    return hilo


@pytest.fixture(autouse=True)
async def _setup_auth_inbox(app, db_session, test_tenant, auth_user_inbox):
    from app.api.dependencies.auth import get_current_user

    async def _override_user():
        return auth_user_inbox
    app.dependency_overrides[get_current_user] = _override_user
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    cleanup_permission_cache()
    yield
    app.dependency_overrides.pop(get_current_user, None)
    cleanup_permission_cache()
