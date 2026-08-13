"""Mission State machine rules and transition validators.
"""

from app.ai.mission.models import MissionState
from app.ai.mission.exceptions import MissionError

class MissionStateMachine:
    """Enforces validation transitions for autonomous mission lifecycles."""

    @staticmethod
    def transition(current: MissionState, new: MissionState) -> MissionState:
        """Asserts state transition safety constraints."""
        valid = {
            MissionState.CREATED: [MissionState.QUEUED],
            MissionState.QUEUED: [MissionState.PLANNING, MissionState.FAILED],
            MissionState.PLANNING: [MissionState.WORKFLOW_GENERATED, MissionState.FAILED],
            MissionState.WORKFLOW_GENERATED: [MissionState.EXECUTING, MissionState.FAILED],
            MissionState.EXECUTING: [MissionState.MONITORING, MissionState.PAUSED, MissionState.FAILED, MissionState.COMPLETED],
            MissionState.MONITORING: [MissionState.EXECUTING, MissionState.PAUSED, MissionState.FAILED, MissionState.COMPLETED],
            MissionState.PAUSED: [MissionState.RESUMED, MissionState.FAILED],
            MissionState.RESUMED: [MissionState.EXECUTING, MissionState.MONITORING, MissionState.FAILED],
            MissionState.COMPLETED: [MissionState.ARCHIVED],
            MissionState.FAILED: [MissionState.QUEUED, MissionState.ARCHIVED],
            MissionState.ARCHIVED: []
        }

        if new in valid.get(current, []):
            return new

        if current == new:
            return current
        raise MissionError(f"Invalid mission lifecycle state transition: from {current} to {new}")
