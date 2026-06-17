"""Tests for AuditoriaService."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.asignacion import Asignacion
from app.models.comunicacion import Comunicacion
from app.models.materia import Materia
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.repositories.base import BaseRepository
from app.schemas.auth import CurrentUser
from app.services.auditoria_service import AuditoriaService


@pytest.fixture
def service(db_session: AsyncSession, test_tenant: Tenant) -> AuditoriaService:
    return AuditoriaService(db_session, test_tenant.id)


class TestGetAccionesPorDia:
    async def test_returns_grouped_counts(
        self,
        db_session: AsyncSession,
        test_tenant: Tenant,
        service: AuditoriaService,
        auth_admin: CurrentUser,
        test_materia: Materia,
    ):
        """Given 2 logs on same day, returns 1 row with total=2."""
        repo = BaseRepository(model=AuditLog, session=db_session, tenant_id=test_tenant.id)
        for _ in range(2):
            await repo.create({
                "actor_id": auth_admin.user_id,
                "materia_id": test_materia.id,
                "accion": "CALIFICACIONES_IMPORTAR",
                "detalle": {},
                "filas_afectadas": 1,
                "ip": "",
                "user_agent": "",
            })
        result = await service.get_acciones_por_dia(
            user_id=auth_admin.user_id,
            roles=auth_admin.roles,
        )
        assert len(result) >= 1
        assert result[0].total == 2

    async def test_empty_when_no_logs(self, service: AuditoriaService):
        result = await service.get_acciones_por_dia()
        assert result == []


class TestGetComunicacionesPorDocente:
    async def test_returns_by_materia(
        self,
        db_session: AsyncSession,
        test_tenant: Tenant,
        service: AuditoriaService,
        auth_admin: CurrentUser,
        test_materia: Materia,
    ):
        from app.models.comunicacion import ComunicacionEstado
        # Comunicacion.enviado_por is FK to usuario.id, need a Usuario
        usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
        usuarios = await usuario_repo.find_by(user_id=auth_admin.user_id)
        assert usuarios, "Usuario should have been created by auth_admin fixture"
        usuario = usuarios[0]

        repo = BaseRepository(model=Comunicacion, session=db_session, tenant_id=test_tenant.id)
        for _ in range(3):
            await repo.create({
                "enviado_por": usuario.id,  # FK to usuario.id, NOT users.id
                "materia_id": test_materia.id,
                "asunto": "Test",
                "cuerpo": "body",
                "destinatario": "a@b.com",
                "destinatario_hash": "x",
                "estado": ComunicacionEstado.ENVIADO.value,
                "lote_id": uuid4(),
            })
        result = await service.get_comunicaciones_por_docente(
            user_id=auth_admin.user_id,
            roles=auth_admin.roles,
        )
        assert len(result) >= 1
        match = [r for r in result if r.materia_id == test_materia.id]
        assert len(match) > 0
        assert match[0].enviado == 3


class TestGetInteraccionesPorDocenteMateria:
    async def test_grupo_por_accion(
        self,
        db_session: AsyncSession,
        test_tenant: Tenant,
        service: AuditoriaService,
        auth_admin: CurrentUser,
        test_materia: Materia,
    ):
        repo = BaseRepository(model=AuditLog, session=db_session, tenant_id=test_tenant.id)
        for accion in ["A", "A", "B"]:
            await repo.create({
                "actor_id": auth_admin.user_id,
                "materia_id": test_materia.id,
                "accion": accion,
                "detalle": {},
                "filas_afectadas": 1,
                "ip": "",
                "user_agent": "",
            })
        result = await service.get_interacciones_por_docente_materia(
            user_id=auth_admin.user_id,
            roles=auth_admin.roles,
        )
        match = [r for r in result if r.docente_id == auth_admin.user_id and r.materia_id == test_materia.id]
        assert len(match) == 1
        acciones = {i.accion for i in match[0].interacciones}
        assert acciones == {"A", "B"}


class TestGetUltimasAcciones:
    async def test_enforces_limit(
        self,
        db_session: AsyncSession,
        test_tenant: Tenant,
        service: AuditoriaService,
        auth_admin: CurrentUser,
        test_materia: Materia,
    ):
        repo = BaseRepository(model=AuditLog, session=db_session, tenant_id=test_tenant.id)
        for i in range(5):
            await repo.create({
                "actor_id": auth_admin.user_id,
                "materia_id": test_materia.id,
                "accion": f"ACTION_{i}",
                "detalle": {},
                "filas_afectadas": 1,
                "ip": "",
                "user_agent": "",
            })
        result = await service.get_ultimas_acciones(
            limit=3,
            user_id=auth_admin.user_id,
            roles=auth_admin.roles,
        )
        assert len(result.items) <= 3
        assert result.limit == 3

    async def test_max_limit(
        self,
        service: AuditoriaService,
    ):
        result = await service.get_ultimas_acciones(limit=2000)
        assert len(result.items) == 0  # no logs, but no error


class TestGetLogAuditoria:
    async def test_offset_and_limit(
        self,
        db_session: AsyncSession,
        test_tenant: Tenant,
        service: AuditoriaService,
        auth_admin: CurrentUser,
        test_materia: Materia,
    ):
        repo = BaseRepository(model=AuditLog, session=db_session, tenant_id=test_tenant.id)
        for i in range(10):
            await repo.create({
                "actor_id": auth_admin.user_id,
                "materia_id": test_materia.id,
                "accion": f"ACTION_{i}",
                "detalle": {},
                "filas_afectadas": 1,
                "ip": "",
                "user_agent": "",
            })
        page = await service.get_log_auditoria(
            offset=0,
            limit=5,
            user_id=auth_admin.user_id,
            roles=auth_admin.roles,
        )
        assert len(page.items) == 5
        assert page.total >= 10

    async def test_total_count(
        self,
        db_session: AsyncSession,
        test_tenant: Tenant,
        service: AuditoriaService,
        auth_admin: CurrentUser,
        test_materia: Materia,
    ):
        repo = BaseRepository(model=AuditLog, session=db_session, tenant_id=test_tenant.id)
        for i in range(3):
            await repo.create({
                "actor_id": auth_admin.user_id,
                "materia_id": test_materia.id,
                "accion": "X",
                "detalle": {},
                "filas_afectadas": 1,
                "ip": "",
                "user_agent": "",
            })
        page = await service.get_log_auditoria(
            offset=0,
            limit=50,
            user_id=auth_admin.user_id,
            roles=auth_admin.roles,
        )
        assert page.total >= 3
