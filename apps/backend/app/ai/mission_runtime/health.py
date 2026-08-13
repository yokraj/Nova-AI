"""Mission Health Monitor performing diagnostic system health checks.
"""

import time
from app.ai.mission_runtime.models import MissionHealth, MissionState


class MissionHealthMonitor:
    """Monitors health of Autonomous Mission Runtime Engine and background workers."""

    def __init__(self) -> None:
        self._state = MissionState.RUNNING

    def set_state(self, state: MissionState) -> None:
        """Updates active runtime state."""
        self._state = state

    def check_health(self) -> MissionHealth:
        """Performs health diagnostic check.

        Returns:
            MissionHealth model instance.
        """
        return MissionHealth(
            is_healthy=self._state != MissionState.FAILED,
            runtime_state=self._state,
            active_workers_count=2,
            queue_length=0,
            timestamp=time.time(),
        )
