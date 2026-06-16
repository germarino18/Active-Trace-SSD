"""Tests for ColoquioService, ReservaService and ResultadoService.

NOTE: All service tests use mocked repositories (not DB). Since
EvaluacionRead / ReservaEvaluacionRead use model_validate, the mock
return values MUST include ALL fields expected by the Pydantic schema:
- EvaluacionRead: id, dictado_id, tipo, instancia, dias_disponibles,
  cupo_maximo, estado, created_at, updated_at
- ReservaEvaluacionRead: id, evaluacion_id, alumno_id, fecha_hora, estado
- ResultadoEvaluacionRead: id, evaluacion_id, alumno_id, nota_final
"""

from unittest.mock import AsyncMock, MagicMock
from types import SimpleNamespace
from datetime import datetime

import pytest
import uuid

from app.schemas.coloquios import (
    EvaluacionCreate,
    EvaluacionUpdate,
    ResultadoEvaluacionCreate,
)
from app.core.exceptions import ValidationException, ForbiddenException, NotFoundException


def _make_ev_ns(**overrides):
    """Build a SimpleNamespace matching EvaluacionRead fields."""
    defaults = {
        "id": uuid.uuid4(),
        "dictado_id": uuid.uuid4(),
        "tenant_id": uuid.uuid4(),
        "tipo": "Coloquio",
        "instancia": "Coloquio Final",
        "dias_disponibles": 10,
        "cupo_maximo": 25,
        "estado": "Activa",
        "created_at": datetime(2026, 6, 16),
        "updated_at": datetime(2026, 6, 16),
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _make_reserva_ns(**overrides):
    """Build a SimpleNamespace matching ReservaEvaluacionRead fields."""
    defaults = {
        "id": uuid.uuid4(),
        "evaluacion_id": uuid.uuid4(),
        "alumno_id": uuid.uuid4(),
        "estado": "Activa",
        "fecha_hora": datetime(2026, 6, 16, 10, 0, 0),
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


# ═══════════════════════════════════════════════════════════════════════
# ColoquioService
# ═══════════════════════════════════════════════════════════════════════


class TestColoquioService:
    """Tests for ColoquioService (ABM, import, metricas)."""

    @pytest.fixture
    def service(self):
        from app.services.coloquios import ColoquioService

        mock_ev_repo = AsyncMock()
        mock_ac_repo = AsyncMock()
        mock_res_repo = AsyncMock()
        mock_audit_repo = AsyncMock()
        mock_session = AsyncMock()
        inst = ColoquioService.__new__(ColoquioService)
        inst._evaluacion_repo = mock_ev_repo
        inst._alumno_convocado_repo = mock_ac_repo
        inst._resultado_repo = mock_res_repo
        inst._audit = MagicMock()
        inst._session = mock_session
        return inst

    @pytest.mark.asyncio
    async def test_crear_evaluacion(self, service):
        """Creating an evaluacion should call repo.create and audit.log."""
        dictado_id = uuid.uuid4()
        data = EvaluacionCreate(
            dictado_id=dictado_id,
            tipo="Coloquio",
            instancia="Coloquio Final",
            cupo_maximo=25,
        )

        fake_evaluacion = _make_ev_ns(
            dictado_id=dictado_id,
            instancia="Coloquio Final",
            cupo_maximo=25,
        )
        service._evaluacion_repo.create = AsyncMock(return_value=fake_evaluacion)
        service._audit.log = AsyncMock()

        current_user = MagicMock()
        request = MagicMock()

        result = await service.crear_evaluacion(
            data, current_user=current_user, request=request
        )

        assert result.instancia == "Coloquio Final"
        assert result.cupo_maximo == 25
        service._evaluacion_repo.create.assert_awaited_once()
        service._audit.log.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_actualizar_evaluacion_cupo_menor_que_reservas(self, service):
        """Updating cupo to a value less than active reservations should be rejected."""
        evaluacion_id = uuid.uuid4()

        mock_ev = MagicMock()
        mock_ev.id = evaluacion_id
        mock_ev.estado = "Activa"
        mock_ev.tenant_id = uuid.uuid4()

        service._evaluacion_repo.find_by_id = AsyncMock(return_value=mock_ev)
        service._evaluacion_repo.update = AsyncMock()

        # Mock reserva_repo inside actualizar_evaluacion (it creates one inline)
        mock_reserva_repo = AsyncMock()
        mock_reserva_repo.count_activas_by_evaluacion = AsyncMock(return_value=10)

        import app.repositories.reserva_evaluacion_repository as rmod

        original = rmod.ReservaEvaluacionRepository
        rmod.ReservaEvaluacionRepository = lambda session, tenant_id: mock_reserva_repo

        try:
            data = EvaluacionUpdate(cupo_maximo=5)
            current_user = MagicMock()
            request = MagicMock()

            with pytest.raises(ValidationException) as exc:
                await service.actualizar_evaluacion(
                    evaluacion_id, data, current_user=current_user, request=request
                )
            assert "cupo" in str(exc.value.message).lower()
        finally:
            rmod.ReservaEvaluacionRepository = original

    @pytest.mark.asyncio
    async def test_cerrar_evaluacion(self, service):
        """Closing an active evaluacion should work."""
        evaluacion_id = uuid.uuid4()
        dictado_id = uuid.uuid4()

        mock_ev = MagicMock()
        mock_ev.id = evaluacion_id
        mock_ev.estado = "Activa"
        mock_ev.dictado_id = dictado_id
        mock_ev.tipo = "Coloquio"
        mock_ev.instancia = "Coloquio Final"
        mock_ev.dias_disponibles = 10
        mock_ev.cupo_maximo = 30
        mock_ev.tenant_id = uuid.uuid4()
        mock_ev.created_at = datetime(2026, 6, 16)
        mock_ev.updated_at = datetime(2026, 6, 16)

        fake_updated = _make_ev_ns(
            id=evaluacion_id,
            dictado_id=dictado_id,
            estado="Cerrada",
        )

        service._evaluacion_repo.find_by_id = AsyncMock(return_value=mock_ev)
        service._evaluacion_repo.update = AsyncMock(return_value=fake_updated)
        service._audit.log = AsyncMock()

        current_user = MagicMock()
        request = MagicMock()

        result = await service.cerrar_evaluacion(
            evaluacion_id, current_user=current_user, request=request
        )

        assert result.estado == "Cerrada"
        service._evaluacion_repo.update.assert_awaited_with(
            evaluacion_id, {"estado": "Cerrada"}
        )
        service._audit.log.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_importar_alumnos_idempotente(self, service):
        """Importing alumnos should be idempotent."""
        evaluacion_id = uuid.uuid4()
        alumno_ids = [uuid.uuid4(), uuid.uuid4()]

        mock_ev = MagicMock()
        mock_ev.id = evaluacion_id
        mock_ev.estado = "Activa"
        mock_ev.tenant_id = uuid.uuid4()

        service._evaluacion_repo.find_by_id = AsyncMock(return_value=mock_ev)
        service._alumno_convocado_repo.bulk_import = AsyncMock(return_value=2)
        service._audit.log = AsyncMock()

        current_user = MagicMock()
        request = MagicMock()

        count = await service.importar_alumnos(
            evaluacion_id, alumno_ids, current_user=current_user, request=request
        )
        assert count == 2

        # Second import — idempotent, returns 0
        service._alumno_convocado_repo.bulk_import = AsyncMock(return_value=0)
        count2 = await service.importar_alumnos(
            evaluacion_id, alumno_ids, current_user=current_user, request=request
        )
        assert count2 == 0

    @pytest.mark.asyncio
    async def test_obtener_evaluacion_not_found(self, service):
        """Getting a non-existent evaluacion should raise NotFoundException."""
        evaluacion_id = uuid.uuid4()
        service._evaluacion_repo.find_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundException) as exc:
            await service.obtener_evaluacion(evaluacion_id)
        assert "Evaluacion" in str(exc.value.message)


# ═══════════════════════════════════════════════════════════════════════
# ReservaService
# ═══════════════════════════════════════════════════════════════════════


class TestReservaService:
    """Tests for ReservaService (reservar, cancelar, listar agenda)."""

    @pytest.fixture
    def service(self):
        from app.services.coloquios.reserva_service import ReservaService

        mock_ev_repo = AsyncMock()
        mock_res_repo = AsyncMock()
        mock_ac_repo = AsyncMock()
        mock_audit_repo = AsyncMock()
        mock_session = AsyncMock()
        inst = ReservaService.__new__(ReservaService)
        inst._evaluacion_repo = mock_ev_repo
        inst._reserva_repo = mock_res_repo
        inst._alumno_convocado_repo = mock_ac_repo
        inst._audit = MagicMock()
        inst._session = mock_session
        return inst

    @pytest.mark.asyncio
    async def test_reservar_con_cupo_disponible(self, service):
        """Reserving with available cupo should succeed."""
        evaluacion_id = uuid.uuid4()
        alumno_id = uuid.uuid4()

        mock_ev = MagicMock()
        mock_ev.id = evaluacion_id
        mock_ev.estado = "Activa"
        mock_ev.cupo_maximo = 30
        mock_ev.tenant_id = uuid.uuid4()

        fake_reserva = _make_reserva_ns(
            evaluacion_id=evaluacion_id,
            alumno_id=alumno_id,
        )

        service._evaluacion_repo.find_by_id = AsyncMock(return_value=mock_ev)
        service._alumno_convocado_repo.exists = AsyncMock(return_value=True)
        service._reserva_repo.count_activas_by_evaluacion = AsyncMock(return_value=5)
        service._reserva_repo.find_by = AsyncMock(return_value=[])
        service._reserva_repo.create = AsyncMock(return_value=fake_reserva)
        service._audit.log = AsyncMock()

        current_user = MagicMock()
        current_user.user_id = alumno_id
        request = MagicMock()

        result = await service.reservar(
            evaluacion_id, current_user=current_user, request=request
        )

        assert result is not None
        assert result.estado == "Activa"
        service._reserva_repo.create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_reservar_cupo_agotado(self, service):
        """Reserving when cupo is full should raise ValidationException."""
        evaluacion_id = uuid.uuid4()

        mock_ev = MagicMock()
        mock_ev.id = evaluacion_id
        mock_ev.estado = "Activa"
        mock_ev.cupo_maximo = 10

        service._evaluacion_repo.find_by_id = AsyncMock(return_value=mock_ev)
        service._alumno_convocado_repo.exists = AsyncMock(return_value=True)
        service._reserva_repo.count_activas_by_evaluacion = AsyncMock(return_value=10)

        current_user = MagicMock()
        current_user.user_id = uuid.uuid4()
        request = MagicMock()

        with pytest.raises(ValidationException) as exc:
            await service.reservar(
                evaluacion_id, current_user=current_user, request=request
            )
        assert "Cupo" in str(exc.value.message)

    @pytest.mark.asyncio
    async def test_reservar_no_convocado(self, service):
        """Reserving without being convocado should raise ForbiddenException."""
        evaluacion_id = uuid.uuid4()

        mock_ev = MagicMock()
        mock_ev.id = evaluacion_id
        mock_ev.estado = "Activa"
        mock_ev.cupo_maximo = 30

        service._evaluacion_repo.find_by_id = AsyncMock(return_value=mock_ev)
        service._alumno_convocado_repo.exists = AsyncMock(return_value=False)

        current_user = MagicMock()
        current_user.user_id = uuid.uuid4()
        request = MagicMock()

        with pytest.raises(ForbiddenException) as exc:
            await service.reservar(
                evaluacion_id, current_user=current_user, request=request
            )
        assert "convocado" in str(exc.value.message).lower() or "habilitado" in str(exc.value.message).lower()

    @pytest.mark.asyncio
    async def test_cancelar_reserva_owner(self, service):
        """Owner can cancel their own reservation."""
        reserva_id = uuid.uuid4()
        alumno_id = uuid.uuid4()
        evaluacion_id = uuid.uuid4()

        mock_reserva = MagicMock()
        mock_reserva.id = reserva_id
        mock_reserva.alumno_id = alumno_id
        mock_reserva.evaluacion_id = evaluacion_id
        mock_reserva.estado = "Activa"
        mock_reserva.tenant_id = uuid.uuid4()

        fake_cancelled = _make_reserva_ns(
            id=reserva_id,
            evaluacion_id=evaluacion_id,
            alumno_id=alumno_id,
            estado="Cancelada",
        )

        service._reserva_repo.find_by_id = AsyncMock(return_value=mock_reserva)
        service._evaluacion_repo.find_by_id = AsyncMock(
            return_value=SimpleNamespace(estado="Activa")
        )
        service._reserva_repo.cancelar = AsyncMock(return_value=fake_cancelled)
        service._audit.log = AsyncMock()

        current_user = MagicMock()
        current_user.user_id = alumno_id
        current_user.roles = ["ALUMNO"]
        request = MagicMock()

        result = await service.cancelar_reserva(
            reserva_id, current_user=current_user, request=request
        )

        assert result is not None
        assert result.estado == "Cancelada"

    @pytest.mark.asyncio
    async def test_cancelar_reserva_not_owner(self, service):
        """Non-owner without gestionar permission should get ForbiddenException."""
        reserva_id = uuid.uuid4()

        mock_reserva = MagicMock()
        mock_reserva.id = reserva_id
        mock_reserva.alumno_id = uuid.uuid4()  # different from current_user
        mock_reserva.evaluacion_id = uuid.uuid4()
        mock_reserva.estado = "Activa"

        service._reserva_repo.find_by_id = AsyncMock(return_value=mock_reserva)
        service._evaluacion_repo.find_by_id = AsyncMock(
            return_value=SimpleNamespace(estado="Activa")
        )

        current_user = MagicMock()
        current_user.user_id = uuid.uuid4()  # not owner
        current_user.roles = ["ALUMNO"]
        request = MagicMock()

        with pytest.raises(ForbiddenException) as exc:
            await service.cancelar_reserva(
                reserva_id, current_user=current_user, request=request
            )
        assert "No puedes" in str(exc.value.message)


# ═══════════════════════════════════════════════════════════════════════
# ResultadoService
# ═══════════════════════════════════════════════════════════════════════


class TestResultadoService:
    """Tests for ResultadoService (registrar resultado)."""

    @pytest.fixture
    def service(self):
        from app.services.coloquios.resultado_service import ResultadoService

        mock_ev_repo = AsyncMock()
        mock_res_repo = AsyncMock()
        mock_ac_repo = AsyncMock()
        mock_audit_repo = AsyncMock()
        mock_session = AsyncMock()
        inst = ResultadoService.__new__(ResultadoService)
        inst._evaluacion_repo = mock_ev_repo
        inst._resultado_repo = mock_res_repo
        inst._alumno_convocado_repo = mock_ac_repo
        inst._audit = MagicMock()
        inst._session = mock_session
        return inst

    @pytest.mark.asyncio
    async def test_registrar_resultado_ok(self, service):
        """Registering a result for a convocado alumno should succeed."""
        data = ResultadoEvaluacionCreate(
            evaluacion_id=uuid.uuid4(),
            alumno_id=uuid.uuid4(),
            nota_final="Aprobado (7)",
        )

        mock_ev = MagicMock()
        mock_ev.id = data.evaluacion_id
        service._evaluacion_repo.find_by_id = AsyncMock(return_value=mock_ev)
        service._alumno_convocado_repo.exists = AsyncMock(return_value=True)
        service._resultado_repo.get_by_evaluacion_alumno = AsyncMock(return_value=None)

        fake_resultado = SimpleNamespace(
            id=uuid.uuid4(),
            evaluacion_id=data.evaluacion_id,
            alumno_id=data.alumno_id,
            nota_final=data.nota_final,
        )
        service._resultado_repo.create = AsyncMock(return_value=fake_resultado)
        service._audit.log = AsyncMock()

        current_user = MagicMock()
        request = MagicMock()

        result = await service.registrar_resultado(
            data, current_user=current_user, request=request
        )

        assert result is not None
        assert result.nota_final == "Aprobado (7)"
        service._resultado_repo.create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_registrar_resultado_duplicado(self, service):
        """Registering a duplicate result should raise ValidationException."""
        data = ResultadoEvaluacionCreate(
            evaluacion_id=uuid.uuid4(),
            alumno_id=uuid.uuid4(),
            nota_final="8",
        )

        mock_ev = MagicMock()
        mock_ev.id = data.evaluacion_id
        service._evaluacion_repo.find_by_id = AsyncMock(return_value=mock_ev)
        service._alumno_convocado_repo.exists = AsyncMock(return_value=True)
        service._resultado_repo.get_by_evaluacion_alumno = AsyncMock(
            return_value=MagicMock(id=uuid.uuid4())
        )

        current_user = MagicMock()
        request = MagicMock()

        with pytest.raises(ValidationException) as exc:
            await service.registrar_resultado(
                data, current_user=current_user, request=request
            )
        assert "ya tiene un resultado" in str(exc.value.message).lower()

    @pytest.mark.asyncio
    async def test_registrar_resultado_no_convocado(self, service):
        """Registering a result for a non-convocado alumno should fail."""
        data = ResultadoEvaluacionCreate(
            evaluacion_id=uuid.uuid4(),
            alumno_id=uuid.uuid4(),
            nota_final="Aprobado",
        )

        mock_ev = MagicMock()
        mock_ev.id = data.evaluacion_id
        service._evaluacion_repo.find_by_id = AsyncMock(return_value=mock_ev)
        service._alumno_convocado_repo.exists = AsyncMock(return_value=False)

        current_user = MagicMock()
        request = MagicMock()

        with pytest.raises(ValidationException) as exc:
            await service.registrar_resultado(
                data, current_user=current_user, request=request
            )
        assert "convocado" in str(exc.value.message).lower()
