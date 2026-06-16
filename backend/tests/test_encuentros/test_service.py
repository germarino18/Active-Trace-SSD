"""Tests for EncuentrosService."""

from datetime import date, datetime, time
from unittest.mock import AsyncMock, MagicMock
from types import SimpleNamespace

import pytest
import uuid

from app.schemas.encuentros import (
    InstanciaEncuentroUpdate,
    SlotEncuentroCreate,
)
from app.core.exceptions import ValidationException


class TestEncuentrosService:
    """Tests for EncuentrosService focusing on business logic."""

    @pytest.fixture
    def service(self):
        from app.services.encuentros import EncuentrosService

        mock_slot_repo = AsyncMock()
        mock_instancia_repo = AsyncMock()
        mock_audit_repo = AsyncMock()
        mock_session = AsyncMock()
        inst = EncuentrosService.__new__(EncuentrosService)
        inst._slot_repo = mock_slot_repo
        inst._instancia_repo = mock_instancia_repo
        inst._audit = MagicMock()
        inst._session = mock_session
        return inst

    @pytest.mark.asyncio
    async def test_crear_slot_recurrente_genera_instancias(self, service):
        """Creating a recurrent slot should generate instances upfront (D1)."""
        dictado_id = uuid.uuid4()
        now = datetime.now()
        slot_data = SlotEncuentroCreate(
            dictado_id=dictado_id,
            titulo="Clase Semanal",
            hora=time(18, 0),
            dia_semana="Lunes",
            fecha_inicio=date(2026, 3, 15),
            cant_semanas=3,
            vig_desde=date(2026, 3, 1),
        )

        # Use an object with real attributes for model_validate
        slot = SimpleNamespace(
            id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            dictado_id=dictado_id,
            asignacion_id=None,
            titulo="Clase Semanal",
            hora=time(18, 0),
            dia_semana="Lunes",
            fecha_inicio=date(2026, 3, 15),
            cant_semanas=3,
            fecha_unica=None,
            meet_url=None,
            vig_desde=date(2026, 3, 1),
            vig_hasta=None,
        )
        service._slot_repo.create = AsyncMock(return_value=slot)
        service._instancia_repo.bulk_create = AsyncMock(return_value=[])
        service._audit.log = AsyncMock()

        current_user = MagicMock()
        current_user.tenant_id = uuid.uuid4()
        request = MagicMock()

        result = await service.crear_slot(
            slot_data, current_user=current_user, request=request
        )

        assert result.titulo == "Clase Semanal"
        service._slot_repo.create.assert_awaited_once()
        service._instancia_repo.bulk_create.assert_awaited_once()
        # Verify bulk_create was called with 3 instances
        call_args = service._instancia_repo.bulk_create.call_args[0][0]
        assert len(call_args) == 3

    @pytest.mark.asyncio
    async def test_crear_slot_cant_semanas_mas_52_rechazado(self, service):
        """Creating a slot with cant_semanas > 52 should be rejected by Pydantic."""
        import pydantic

        dictado_id = uuid.uuid4()
        with pytest.raises(pydantic.ValidationError) as exc:
            SlotEncuentroCreate(
                dictado_id=dictado_id,
                titulo="Slot Invalido",
                hora=time(18, 0),
                dia_semana="Lunes",
                fecha_inicio=date(2026, 3, 15),
                cant_semanas=100,
                vig_desde=date(2026, 3, 1),
            )
        assert "cant_semanas" in str(exc.value)

    @pytest.mark.asyncio
    async def test_crear_slot_sin_fecha_unica_rechazado(self, service):
        """Creating a slot with cant_semanas=0 and no fecha_unica should be rejected."""
        dictado_id = uuid.uuid4()
        slot_data = SlotEncuentroCreate(
            dictado_id=dictado_id,
            titulo="Slot Sin Fecha",
            hora=time(18, 0),
            dia_semana="Lunes",
            fecha_inicio=date(2026, 3, 15),
            cant_semanas=0,
            fecha_unica=None,
            vig_desde=date(2026, 3, 1),
        )

        current_user = MagicMock()
        request = MagicMock()

        with pytest.raises(ValidationException) as exc:
            await service.crear_slot(
                slot_data, current_user=current_user, request=request
            )
        assert "fecha_unica" in str(exc.value.details)

    @pytest.mark.asyncio
    async def test_editar_instancia_transicion_valida(self, service):
        """Editing instance from Programado to Realizado should work."""
        instancia_id = uuid.uuid4()
        now = datetime.now()

        # Build fake instancia with real values for model_validate
        fake_instancia = SimpleNamespace(
            id=instancia_id,
            slot_id=uuid.uuid4(),
            dictado_id=uuid.uuid4(),
            asignacion_id=None,
            fecha=date(2026, 3, 15),
            hora=time(18, 0),
            titulo="Clase 1",
            estado="Realizado",
            meet_url=None,
            video_url="https://vimeo.com/123",
            comentario="Buena clase",
        )

        mock_instancia = MagicMock()
        mock_instancia.id = instancia_id
        mock_instancia.estado = "Programado"
        mock_instancia.slot_id = uuid.uuid4()

        service._instancia_repo.find_by_id = AsyncMock(return_value=mock_instancia)
        service._instancia_repo.update = AsyncMock(return_value=fake_instancia)
        service._audit.log = AsyncMock()

        current_user = MagicMock()
        request = MagicMock()

        data = InstanciaEncuentroUpdate(
            estado="Realizado",
            video_url="https://vimeo.com/123",
            comentario="Buena clase",
        )

        result = await service.editar_instancia(
            instancia_id, data, current_user=current_user, request=request
        )

        assert result is not None
        assert result.estado == "Realizado"
        assert result.video_url == "https://vimeo.com/123"
        service._instancia_repo.update.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_editar_instancia_transicion_invalida(self, service):
        """Editing instance from Cancelado to Realizado should be rejected."""
        instancia_id = uuid.uuid4()
        mock_instancia = MagicMock()
        mock_instancia.id = instancia_id
        mock_instancia.estado = "Cancelado"
        mock_instancia.slot_id = uuid.uuid4()

        service._instancia_repo.find_by_id = AsyncMock(return_value=mock_instancia)

        current_user = MagicMock()
        request = MagicMock()

        data = InstanciaEncuentroUpdate(estado="Realizado")

        with pytest.raises(ValidationException) as exc:
            await service.editar_instancia(
                instancia_id, data, current_user=current_user, request=request
            )
        assert "Transición inválida" in str(exc.value.message)

    @pytest.mark.asyncio
    async def test_generar_bloque_html(self, service):
        """Generate HTML block should return formatted HTML."""
        dictado_id = uuid.uuid4()

        mock_inst1 = MagicMock()
        mock_inst1.fecha = date(2026, 3, 15)
        mock_inst1.hora = time(18, 0)
        mock_inst1.titulo = "Clase 1"
        mock_inst1.meet_url = "https://meet.example.com/1"
        mock_inst1.video_url = None
        mock_inst1.estado = "Programado"

        mock_inst2 = MagicMock()
        mock_inst2.fecha = date(2026, 3, 22)
        mock_inst2.hora = time(18, 0)
        mock_inst2.titulo = "Clase 2"
        mock_inst2.meet_url = "https://meet.example.com/2"
        mock_inst2.video_url = "https://vimeo.com/2"
        mock_inst2.estado = "Realizado"

        service._instancia_repo.list_by_dictado = AsyncMock(
            return_value=[mock_inst1, mock_inst2]
        )

        result = await service.generar_bloque_html(dictado_id)

        assert result.total_encuentros == 2
        assert "<table" in result.html
        assert "meet.example.com" in result.html
        assert "Grabación" in result.html
