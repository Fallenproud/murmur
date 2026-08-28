from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
import threading
import time


class SessionState(StrEnum):
    IDLE = "idle"
    ARMING = "arming"
    LISTENING = "listening"
    FINALIZING = "finalizing"
    TRANSCRIBING = "transcribing"
    REFINING = "refining"
    VALIDATING = "validating"
    INSERTING = "inserting"
    COMPLETE = "complete"
    CANCELLED = "cancelled"
    ERROR = "error"


_ALLOWED: dict[SessionState, set[SessionState]] = {
    SessionState.IDLE: {SessionState.ARMING},
    SessionState.ARMING: {SessionState.LISTENING, SessionState.CANCELLED, SessionState.ERROR},
    SessionState.LISTENING: {SessionState.FINALIZING, SessionState.CANCELLED, SessionState.ERROR},
    SessionState.FINALIZING: {SessionState.TRANSCRIBING, SessionState.CANCELLED, SessionState.ERROR},
    SessionState.TRANSCRIBING: {SessionState.REFINING, SessionState.VALIDATING, SessionState.COMPLETE, SessionState.ERROR},
    SessionState.REFINING: {SessionState.VALIDATING, SessionState.ERROR},
    SessionState.VALIDATING: {SessionState.INSERTING, SessionState.COMPLETE, SessionState.ERROR},
    SessionState.INSERTING: {SessionState.COMPLETE, SessionState.ERROR},
    SessionState.COMPLETE: {SessionState.IDLE},
    SessionState.CANCELLED: {SessionState.IDLE},
    SessionState.ERROR: {SessionState.IDLE},
}


@dataclass(slots=True)
class StateTransition:
    previous: SessionState
    current: SessionState
    at: float = field(default_factory=time.monotonic)


class SessionStateMachine:
    """Thread-safe finite-state machine shared by daemon and UI adapters."""

    def __init__(self) -> None:
        self._state = SessionState.IDLE
        self._lock = threading.RLock()
        self._history: list[StateTransition] = []

    @property
    def state(self) -> SessionState:
        with self._lock:
            return self._state

    @property
    def history(self) -> tuple[StateTransition, ...]:
        with self._lock:
            return tuple(self._history)

    def transition(self, target: SessionState) -> StateTransition:
        with self._lock:
            if target == self._state:
                return StateTransition(self._state, target)
            if target not in _ALLOWED[self._state]:
                raise RuntimeError(f"invalid Murmur session transition: {self._state} -> {target}")
            transition = StateTransition(self._state, target)
            self._state = target
            self._history.append(transition)
            return transition

    def reset(self) -> None:
        with self._lock:
            if self._state == SessionState.IDLE:
                return
            if SessionState.IDLE not in _ALLOWED[self._state]:
                self._state = SessionState.ERROR
            self.transition(SessionState.IDLE)
