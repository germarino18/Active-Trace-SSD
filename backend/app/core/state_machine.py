"""Generic state machine helper for validating entity state transitions."""

from enum import Enum
from typing import Callable


class TransitionError(ValueError):
    """Raised when an invalid state transition is attempted."""

    def __init__(self, from_state: Enum, to_state: Enum):
        self.from_state = from_state
        self.to_state = to_state
        super().__init__(
            f"Cannot transition from {from_state.value} to {to_state.value}"
        )


class StateMachine:
    """Validates state transitions for an enum-type state field.

    Usage:
        sm = StateMachine(
            state_enum=ComunicacionEstado,
            initial=ComunicacionEstado.PENDIENTE,
            transitions={
                ComunicacionEstado.PENDIENTE: [ComunicacionEstado.ENVIANDO],
            },
        )
        sm.validate_transition(current, target)  # raises TransitionError if invalid
    """

    def __init__(
        self,
        state_enum: type[Enum],
        initial: Enum,
        transitions: dict[Enum, list[Enum]],
        on_transition: dict[Enum, Callable] | None = None,
    ):
        self._state_enum = state_enum
        self._initial = initial
        self._transitions = transitions
        self._on_transition = on_transition or {}

    def validate_transition(self, from_state: Enum, to_state: Enum) -> None:
        """Validate that a transition from `from_state` to `to_state` is allowed.

        Raises TransitionError if the transition is invalid.
        """
        allowed = self._transitions.get(from_state, [])
        if to_state not in allowed:
            raise TransitionError(from_state=from_state, to_state=to_state)

    def apply_transition(self, from_state: Enum, to_state: Enum) -> None:
        """Validate and apply side effects of a transition.

        Runs the on_transition callback for the target state if one exists.
        """
        self.validate_transition(from_state, to_state)
        callback = self._on_transition.get(to_state)
        if callback:
            callback()

    @property
    def initial(self) -> Enum:
        return self._initial

    @property
    def allowed_transitions(self) -> dict[Enum, list[Enum]]:
        return dict(self._transitions)
