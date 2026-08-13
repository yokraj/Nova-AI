"""Mission Manager controlling long-running mission lifecycle and persistent store.
"""

from typing import Any, Dict, List, Optional
import time
import uuid
from app.ai.mission_runtime.interfaces import IMissionManager
from app.ai.mission_runtime.models import (
    MissionPriority,
    MissionRecord,
    MissionState,
    TaskItem,
    WorkflowDefinition,
    WorkflowType,
)


class MissionManager(IMissionManager):
    """Mission Manager handling mission registration, state updates, cloning, and history."""

    def __init__(self) -> None:
        self._missions: Dict[str, MissionRecord] = {}

    async def create_mission(self, name: str, goal: str, **kwargs: Any) -> MissionRecord:
        """Creates a new long-running mission and seeds its workflow.

        Args:
            name: Human-readable mission title.
            goal: Natural language goal prompt.
            **kwargs: Priority, initial tasks, cron.

        Returns:
            MissionRecord model instance.
        """
        priority = kwargs.get("priority", MissionPriority.NORMAL)
        tasks = kwargs.get("tasks", [
            TaskItem(title=f"Plan execution strategy for: {goal}", action_type="planning"),
            TaskItem(title=f"Execute core autonomous workflow steps", action_type="swarm_execution"),
            TaskItem(title=f"Verify outputs & learn from execution", action_type="verification"),
        ])

        wf = WorkflowDefinition(
            name=f"Workflow_{name}",
            type=kwargs.get("workflow_type", WorkflowType.SEQUENTIAL),
            tasks=tasks,
        )

        mission = MissionRecord(
            name=name,
            goal=goal,
            state=MissionState.CREATED,
            priority=priority,
            workflow=wf,
        )

        self._missions[mission.mission_id] = mission
        return mission

    async def pause_mission(self, mission_id: str) -> MissionRecord:
        """Pauses running mission state."""
        mission = self._missions.get(mission_id)
        if mission:
            mission.state = MissionState.PAUSED
            mission.updated_at = time.time()
            return mission
        raise ValueError(f"Mission '{mission_id}' not found.")

    async def resume_mission(self, mission_id: str) -> MissionRecord:
        """Resumes paused mission execution."""
        mission = self._missions.get(mission_id)
        if mission:
            mission.state = MissionState.RUNNING
            mission.updated_at = time.time()
            return mission
        raise ValueError(f"Mission '{mission_id}' not found.")

    async def cancel_mission(self, mission_id: str) -> MissionRecord:
        """Cancels mission execution."""
        mission = self._missions.get(mission_id)
        if mission:
            mission.state = MissionState.FAILED
            mission.updated_at = time.time()
            return mission
        raise ValueError(f"Mission '{mission_id}' not found.")

    async def restart_mission(self, mission_id: str) -> MissionRecord:
        """Restarts mission from initial task."""
        mission = self._missions.get(mission_id)
        if mission:
            mission.current_task_index = 0
            mission.state = MissionState.RUNNING
            for task in mission.workflow.tasks:
                task.status = "pending"
            mission.updated_at = time.time()
            return mission
        raise ValueError(f"Mission '{mission_id}' not found.")

    async def clone_mission(self, mission_id: str) -> MissionRecord:
        """Clones an existing mission definition."""
        source = self._missions.get(mission_id)
        if not source:
            raise ValueError(f"Mission '{mission_id}' not found.")

        cloned = MissionRecord(
            name=f"Copy of {source.name}",
            goal=source.goal,
            state=MissionState.CREATED,
            priority=source.priority,
            workflow=source.workflow.model_copy(deep=True),
        )
        self._missions[cloned.mission_id] = cloned
        return cloned

    async def archive_mission(self, mission_id: str) -> MissionRecord:
        """Archives completed or cancelled mission."""
        mission = self._missions.get(mission_id)
        if mission:
            mission.state = MissionState.ARCHIVED
            mission.updated_at = time.time()
            return mission
        raise ValueError(f"Mission '{mission_id}' not found.")

    async def delete_mission(self, mission_id: str) -> bool:
        """Deletes mission from memory store."""
        if mission_id in self._missions:
            del self._missions[mission_id]
            return True
        return False

    async def get_mission(self, mission_id: str) -> Optional[MissionRecord]:
        """Retrieves mission record by ID."""
        return self._missions.get(mission_id)

    async def list_missions(self) -> List[MissionRecord]:
        """Returns all registered mission records."""
        return list(self._missions.values())

    async def get_statistics(self) -> Dict[str, int]:
        """Calculates mission status counters."""
        stats = {
            "total": len(self._missions),
            "running": 0,
            "paused": 0,
            "completed": 0,
            "failed": 0,
        }
        for m in self._missions.values():
            if m.state == MissionState.RUNNING:
                stats["running"] += 1
            elif m.state == MissionState.PAUSED:
                stats["paused"] += 1
            elif m.state == MissionState.COMPLETED:
                stats["completed"] += 1
            elif m.state == MissionState.FAILED:
                stats["failed"] += 1
        return stats
