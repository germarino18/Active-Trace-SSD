"""Tests for MensajeriaService."""
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.hilo_conversacion import HiloConversacion
from app.models.hilo_participante import HiloParticipante
from app.models.mensaje import Mensaje
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.repositories.base import BaseRepository
from app.schemas.auth import CurrentUser
from app.services.mensajeria_service import MensajeriaService


@pytest.fixture
def service(db_session: AsyncSession, test_tenant: Tenant) -> MensajeriaService:
    return MensajeriaService(db=db_session, tenant_id=test_tenant.id)


class TestListHilos:
    async def test_returns_hilos(
        self,
        service: MensajeriaService,
        auth_usuario: Usuario,
        test_hilo,
    ):
        hilos = await service.list_hilos(auth_usuario.id)
        assert len(hilos) == 1
        assert hilos[0].asunto == "Test conversation"

    async def test_empty_inbox(
        self,
        service: MensajeriaService,
        db_session: AsyncSession,
        test_tenant: Tenant,
    ):
        """Usuario sin hilos recibe lista vacía."""
        from app.models.user import User
        from uuid import uuid4

        user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
        user = await user_repo.create({
            "email": f"empty-{uuid4().hex[:8]}@test.com",
            "password_hash": "hash",
            "display_name": "Empty",
            "is_active": True,
        })
        from app.schemas.auth import CurrentUser
        empty_user = CurrentUser(user_id=user.id, tenant_id=test_tenant.id, roles=["ALUMNO"])
        hilos = await service.list_hilos(empty_user.user_id)
        assert hilos == []


class TestGetHilo:
    async def test_returns_messages(
        self,
        service: MensajeriaService,
        auth_usuario: Usuario,
        test_hilo,
    ):
        mensajes = await service.get_hilo(test_hilo.id, auth_usuario.id)
        assert len(mensajes) >= 1
        assert "Hola" in mensajes[0].contenido

    async def test_non_participant_returns_404(
        self,
        service: MensajeriaService,
        test_hilo,
        db_session: AsyncSession,
        test_tenant: Tenant,
    ):
        from app.models.user import User

        user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
        user = await user_repo.create({
            "email": f"outsider-{uuid4().hex[:8]}@test.com",
            "password_hash": "hash",
            "display_name": "Outsider",
            "is_active": True,
        })
        # Crear Usuario para el outsider (necesario para la FK)
        usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
        usuario = await usuario_repo.create({
            "user_id": user.id,
            "nombre": "Outsider",
            "apellidos": "User",
        })
        with pytest.raises(NotFoundException):
            await service.get_hilo(test_hilo.id, usuario.id)

    async def test_nonexistent_hilo_returns_404(
        self,
        service: MensajeriaService,
        auth_usuario: Usuario,
    ):
        with pytest.raises(NotFoundException):
            await service.get_hilo(uuid4(), auth_usuario.id)


class TestResponder:
    async def test_responder_creates_message(
        self,
        service: MensajeriaService,
        auth_usuario: Usuario,
        test_hilo,
    ):
        mensaje = await service.responder(
            test_hilo.id,
            auth_usuario.id,
            "Gracias por el mensaje",
        )
        assert mensaje.contenido == "Gracias por el mensaje"
        assert mensaje.remitente_id == auth_usuario.id

    async def test_responder_non_participant_404(
        self,
        service: MensajeriaService,
        test_hilo,
        db_session: AsyncSession,
        test_tenant: Tenant,
    ):
        from app.models.user import User

        user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
        user = await user_repo.create({
            "email": f"outsider2-{uuid4().hex[:8]}@test.com",
            "password_hash": "hash",
            "display_name": "Outsider2",
            "is_active": True,
        })
        usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
        usuario = await usuario_repo.create({
            "user_id": user.id,
            "nombre": "Outsider2",
            "apellidos": "User",
        })
        with pytest.raises(NotFoundException):
            await service.responder(test_hilo.id, usuario.id, "Hola")

    async def test_responder_nonexistent_hilo_404(
        self,
        service: MensajeriaService,
        auth_usuario: Usuario,
    ):
        with pytest.raises(NotFoundException):
            await service.responder(uuid4(), auth_usuario.id, "Hola")
