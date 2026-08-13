"""Mock Mission Runtime Provider for offline unit tests and CI integration.
"""

from typing import Any, Dict, List, Optional
from app.ai.mission_runtime.models import (
    MissionHealth,
    MissionPriority,
    MissionRecord,
    MissionState,
    ProgressReport,
    TaskItem,
    WorkflowDefinition,
)


class MockMissionRuntimeProvider:
    """Mock Mission Runtime Provider returning deterministic test data."""

    async def create_mission(self, name: str, goal: str, **kwargs: Any) -> MissionRecord:
        """Returns mock MissionRecord."""
        wf = WorkflowDefinition(name=f"MockWF_{name}", tasks=[TaskItem(title="Mock Task")])
        return MissionRecord(
            mission_id="msn_mock123",
            name=name,
            goal=goal,
            state=MissionState.RUNNING,
            workflow=wf,
        )

    async def mission_progress(self, mission_id: str) -> ProgressReport:
        """Returns mock ProgressReport."""
        return ProgressReport(
            mission_id=mission_id,
            percent_complete=50.0,
            eta_seconds=60.0,
            completed_tasks=1,
            remaining_tasks=1,
            status_summary="Mock mission running smoothly.",
        )

    async def check_health(self) -> MissionHealth:
        """Returns mock MissionHealth."""
        return MissionHealth(
            is_healthy=True,
            runtime_state=MissionState.RUNNING,
            active_workers_count=1,
        )
