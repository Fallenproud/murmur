import pytest

from murmur_core.state import SessionState, SessionStateMachine


def test_happy_path_session_lifecycle():
    machine = SessionStateMachine()
    for state in (
        SessionState.ARMING,
        SessionState.LISTENING,
        SessionState.FINALIZING,
        SessionState.TRANSCRIBING,
        SessionState.REFINING,
        SessionState.VALIDATING,
        SessionState.INSERTING,
        SessionState.COMPLETE,
        SessionState.IDLE,
    ):
        machine.transition(state)
    assert machine.state is SessionState.IDLE


def test_invalid_transition_is_rejected():
    machine = SessionStateMachine()
    with pytest.raises(RuntimeError):
        machine.transition(SessionState.INSERTING)
