"""Execution Monitor tracking real-time status across running, waiting, completed, cancelled, and failed tasks."""

from typing import Dict, List
import structlog

from app.ai.execution.models import ExecutionState, MissionExecutionPlan

logger = structlog.get_logger("execution_monitor")


class ExecutionMonitor:
    """Real-time monitoring service tracking mission distributions."""

    def __init__(self) -> None:
        self._tracked: Dict[str, MissionExecutionPlan] = {}

    def track(self, plan: MissionExecutionPlan) -> None:
        """Register plan for monitoring."""
        self._tracked[plan.mission_id] = plan

    def get_summary(self) -> Dict[str, int]:
        """Return counts by execution state."""
        counts = {
            "running": 0,
            "waiting": 0,
            "completed": 0,
            "cancelled": 0,
            "failed": 0,
        }
        for p in self._tracked.values():
            st = p.state.value
            if st == "running":
                counts["running"] += 1
            elif st in ("waiting_approval", "pending", "paused"):
                counts["waiting"] += 1
            elif st == "completed":
                counts["completed"] += 1
            elif st == "cancelled":
                counts["cancelled"] += 1
            elif st in ("failed", "rolled_back"):
                counts["failed"] += 1

        return counts
