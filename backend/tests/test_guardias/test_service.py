"""Tests for GuardiasService."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from types import SimpleNamespace

import pytest
import uuid

from app.core.exceptions import NotFoundException
from app.schemas.guardias import GuardiaCreate, GuardiaUpdate


class TestGuardiasService:
    """Tests for GuardiasService focusing on business logic."""

    @pytest.fixture
    def service(self):
        from app.services.guardias import GuardiasService

        mock_repo = AsyncMock()
        mock_audit_repo = AsyncMock()
        mock_session = AsyncMock()
        inst = GuardiasService.__new__(GuardiasService)
        inst._repo = mock_repo
        inst._audit = MagicMock()
        inst._session = mock_session
        return inst

    @pytest.mark.asyncio
    async def test_registrar_guardia_ok(self, service):
        """Registering a guardia should succeed."""
        dictado_id = uuid.uuid4()
        asignacion_id = uuid.uuid4()
        data = GuardiaCreate(
            asignacion_id=asignacion_id,
            dictado_id=dictado_id,
            dia="Martes",
            horario="14:00–14:45",
        )

        fake = SimpleNamespace(
            id=uuid.uuid4(),
            dictado_id=dictado_id,
            asignacion_id=asignacion_id,
            dia="Martes",
            horario="14:00–14:45",
            estado="Pendiente",
            comentarios=None,
            creada_at=datetime.now(),
        )

        service._repo.create = AsyncMock(return_value=fake)
        service._audit.log = AsyncMock()

        current_user = MagicMock()
        request = MagicMock()

        result = await service.registrar(
            data, current_user=current_user, request=request
        )

        assert result.dia == "Martes"
        assert result.estado == "Pendiente"
        service._repo.create.assert_awaited_once()
        service._audit.log.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_editar_guardia_ok(self, service):
        """Editing a guardia should succeed."""
        guardia_id = uuid.uuid4()
        data = GuardiaUpdate(estado="Realizada", comentarios="Todo ok")

        fake = SimpleNamespace(
            id=guardia_id,
            asignacion_id=uuid.uuid4(),
            dictado_id=uuid.uuid4(),
            dia="Lunes",
            horario="09:00–09:45",
            estado="Realizada",
            comentarios="Todo ok",
            creada_at=datetime.now(),
        )

        service._repo.find_by_id = AsyncMock(return_value=MagicMock())
        service._repo.update = AsyncMock(return_value=fake)

        current_user = MagicMock()
        request = MagicMock()

        result = await service.editar(
            guardia_id, data, current_user=current_user, request=request
        )

        assert result is not None
        assert result.estado == "Realizada"
        assert result.comentarios == "Todo ok"
        service._repo.update.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_editar_guardia_not_found(self, service):
        """Editing a non-existent guardia should raise NotFoundException."""
        guardia_id = uuid.uuid4()
        data = GuardiaUpdate(estado="Cancelada")

        service._repo.find_by_id = AsyncMock(return_value=None)

        current_user = MagicMock()
        request = MagicMock()

        with pytest.raises(NotFoundException):
            await service.editar(
                guardia_id, data, current_user=current_user, request=request
            )

    @pytest.mark.asyncio
    async def test_listar_guardias(self, service):
        """Listing guardias should work."""
        guardia_id = uuid.uuid4()
        dictado_id = uuid.uuid4()

        fake = SimpleNamespace(
            id=guardia_id,
            asignacion_id=uuid.uuid4(),
            dictado_id=dictado_id,
            dia="Lunes",
            horario="09:00–09:45",
            estado="Pendiente",
            comentarios=None,
            creada_at=datetime.now(),
        )

        service._repo.list_by_tenant = AsyncMock(return_value=[fake])

        result = await service.listar(dictado_id=dictado_id)

        assert len(result) == 1
        assert result[0].dia == "Lunes"
        service._repo.list_by_tenant.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_exportar_csv(self, service):
        """Export guardias to CSV should return StreamingResponse."""
        fake = SimpleNamespace(
            id=uuid.uuid4(),
            dictado_id=uuid.uuid4(),
            asignacion_id=uuid.uuid4(),
            dia="Martes",
            horario="14:00–14:45",
            estado="Realizada",
            comentarios="Completada",
        )

        service._repo.list_for_export = AsyncMock(return_value=[fake])
        service._resolver_nombre_materia = AsyncMock(return_value="Matemática")
        service._resolver_nombre_docente = AsyncMock(return_value="Juan Pérez")

        result = await service.exportar_csv()

        from fastapi.responses import StreamingResponse
        assert isinstance(result, StreamingResponse)
        assert "text/csv" in result.media_type
