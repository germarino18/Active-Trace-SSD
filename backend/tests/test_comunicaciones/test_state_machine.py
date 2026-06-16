"""Tests for the StateMachine helper for Comunicacion estados."""

import pytest

from app.core.state_machine import StateMachine, TransitionError
from app.models.comunicacion import ComunicacionEstado


@pytest.fixture
def sm() -> StateMachine:
    return StateMachine(
        state_enum=ComunicacionEstado,
        initial=ComunicacionEstado.PENDIENTE,
        transitions={
            ComunicacionEstado.PENDIENTE: [
                ComunicacionEstado.ENVIANDO,
                ComunicacionEstado.CANCELADO,
            ],
            ComunicacionEstado.ENVIANDO: [
                ComunicacionEstado.ENVIADO,
                ComunicacionEstado.ERROR,
            ],
        },
        on_transition={
            ComunicacionEstado.ENVIADO: lambda: None,  # sets enviado_at
        },
    )


@pytest.mark.asyncio
async def test_valid_transition_pendiente_to_enviando(sm: StateMachine):
    sm.validate_transition(ComunicacionEstado.PENDIENTE, ComunicacionEstado.ENVIANDO)
    # No exception = pass


@pytest.mark.asyncio
async def test_valid_transition_pendiente_to_cancelado(sm: StateMachine):
    sm.validate_transition(ComunicacionEstado.PENDIENTE, ComunicacionEstado.CANCELADO)


@pytest.mark.asyncio
async def test_valid_transition_enviando_to_enviado(sm: StateMachine):
    sm.validate_transition(ComunicacionEstado.ENVIANDO, ComunicacionEstado.ENVIADO)


@pytest.mark.asyncio
async def test_valid_transition_enviando_to_error(sm: StateMachine):
    sm.validate_transition(ComunicacionEstado.ENVIANDO, ComunicacionEstado.ERROR)


@pytest.mark.asyncio
async def test_invalid_transition_pendiente_to_enviado(sm: StateMachine):
    with pytest.raises(TransitionError, match="Cannot transition from Pendiente to Enviado"):
        sm.validate_transition(ComunicacionEstado.PENDIENTE, ComunicacionEstado.ENVIADO)


@pytest.mark.asyncio
async def test_invalid_transition_enviado_to_cancelado(sm: StateMachine):
    with pytest.raises(TransitionError):
        sm.validate_transition(ComunicacionEstado.ENVIADO, ComunicacionEstado.CANCELADO)


@pytest.mark.asyncio
async def test_invalid_transition_cancelado_to_enviando(sm: StateMachine):
    sm.validate_transition(ComunicacionEstado.PENDIENTE, ComunicacionEstado.CANCELADO)
    with pytest.raises(TransitionError):
        sm.validate_transition(ComunicacionEstado.CANCELADO, ComunicacionEstado.ENVIANDO)


@pytest.mark.asyncio
async def test_invalid_transition_error_to_enviado(sm: StateMachine):
    with pytest.raises(TransitionError):
        sm.validate_transition(ComunicacionEstado.ERROR, ComunicacionEstado.ENVIADO)
