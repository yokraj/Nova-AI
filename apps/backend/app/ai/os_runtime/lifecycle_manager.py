"""Lifecycle Manager controlling AI Operating System state transitions and emergency stops.
"""

from typing import Any, Dict
from app.ai.os_runtime.models import OSState


class LifecycleManager:
    """Manages AI Operating System state transitions, pause/resume, maintenance, safe mode, and emergency kill switches."""

    def __init__(self) -> None:
        self._current_state = OSState.RUNNING

    async def get_state(self) -> OSState:
        """Returns current OS lifecycle state."""
        return self._current_state

    async def set_state(self, new_state: OSState) -> OSState:
        """Transitions OS state to target lifecycle state."""
        self._current_state = new_state
        return self._current_state

    async def emergency_stop(self) -> Dict[str, Any]:
        """Activates emergency kill switch, pausing all executions immediately."""
        self._current_state = OSState.EMERGENCY_STOP
        return {
            "state": self._current_state,
            "kill_switch_activated": True,
            "status": "EMERGENCY_STOP_ENFORCED",
        }
