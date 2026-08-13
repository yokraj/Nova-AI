"""Status Manager querying active and historical mission statuses."""

from typing import Dict, List, Optional
import structlog

from app.ai.execution.models import MissionExecutionPlan

logger = structlog.get_logger("execution_status_manager")


class StatusManager:
    """Manages active and completed mission status querying."""

    def __init__(self) -> None:
        self._history: Dict[str, MissionExecutionPlan] = {}

    def store_plan(self, plan: MissionExecutionPlan) -> None:
        """Store or update mission plan in history."""
        self._history[plan.mission_id] = plan

    def get_status(self, mission_id: str) -> Optional[MissionExecutionPlan]:
        """Query status of a specific mission."""
        return self._history.get(mission_id)

    def list_active(self) -> List[MissionExecutionPlan]:
        """List active running/pending missions."""
        return [
            p for p in self._history.values()
            if p.state.value in ("running", "pending", "waiting_approval", "paused")
        ]

    def list_history(self) -> List[MissionExecutionPlan]:
        """List all historical missions."""
        return list(self._history.values())
