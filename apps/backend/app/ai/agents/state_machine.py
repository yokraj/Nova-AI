"""Lifecycle State Machine governing transitions between runtime statuses.
"""

from app.ai.agents.exceptions import AgentStateError

class AgentStateValue:
    """Consolidated state constants representing the agent execution lifecycle."""
    CREATED = "CREATED"
    INITIALIZING = "INITIALIZING"
    STARTING = "STARTING"
    READY = "READY"
    BUSY = "BUSY"
    WAITING = "WAITING"
    IDLE = "IDLE"
    PAUSED = "PAUSED"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    FAILED = "FAILED"

class AgentStateMachine:
    """Tracks current states and validates requested lifecycle transitions."""

    def __init__(self, initial_state: str = AgentStateValue.CREATED) -> None:
        self._current_state = initial_state
        self._transitions = {
            AgentStateValue.CREATED: {AgentStateValue.INITIALIZING, AgentStateValue.FAILED},
            AgentStateValue.INITIALIZING: {AgentStateValue.STARTING, AgentStateValue.READY, AgentStateValue.FAILED},
            AgentStateValue.STARTING: {AgentStateValue.READY, AgentStateValue.FAILED},
            AgentStateValue.READY: {
                AgentStateValue.BUSY, AgentStateValue.IDLE, AgentStateValue.PAUSED, AgentStateValue.STOPPING, AgentStateValue.FAILED
            },
            AgentStateValue.BUSY: {
                AgentStateValue.READY, AgentStateValue.WAITING, AgentStateValue.IDLE, AgentStateValue.FAILED, AgentStateValue.STOPPING
            },
            AgentStateValue.WAITING: {AgentStateValue.BUSY, AgentStateValue.READY, AgentStateValue.FAILED},
            AgentStateValue.IDLE: {AgentStateValue.BUSY, AgentStateValue.PAUSED, AgentStateValue.STOPPING, AgentStateValue.FAILED},
            AgentStateValue.PAUSED: {AgentStateValue.READY, AgentStateValue.BUSY, AgentStateValue.IDLE, AgentStateValue.FAILED},
            AgentStateValue.STOPPING: {AgentStateValue.STOPPED, AgentStateValue.FAILED},
            AgentStateValue.STOPPED: {AgentStateValue.STARTING, AgentStateValue.CREATED, AgentStateValue.FAILED},
            AgentStateValue.FAILED: {AgentStateValue.INITIALIZING, AgentStateValue.CREATED}
        }

    @property
    def current_state(self) -> str:
        """Returns active state string identifier."""
        return self._current_state

    def transition_to(self, new_state: str) -> None:
        """Transitions current state, validating boundary rules."""
        allowed = self._transitions.get(self._current_state, set())
        if new_state not in allowed:
            raise AgentStateError(
                f"Illegal state transition requested: from '{self._current_state}' to '{new_state}'."
            )
        self._current_state = new_state
