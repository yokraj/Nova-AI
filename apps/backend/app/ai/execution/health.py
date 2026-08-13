"""Execution Health Monitor checking sub-system health status."""

from typing import Any
from app.ai.execution.models import ExecutionHealth


class ExecutionHealthMonitor:
    """Evaluates composite health across queue, scheduler, checkpoint manager, and resource manager."""

    def __init__(
        self,
        queue: Any,
        checkpoint_manager: Any,
        resource_manager: Any,
    ) -> None:
        self.queue = queue
        self.checkpoint_manager = checkpoint_manager
        self.resource_manager = resource_manager

    def check_health(self) -> ExecutionHealth:
        """Evaluate status report across components."""
        components = {
            "queue": "online" if self.queue else "offline",
            "checkpoint_manager": "online" if self.checkpoint_manager else "offline",
            "resource_manager": "online" if self.resource_manager else "offline",
        }
        overall = "healthy" if all(v == "online" for v in components.values()) else "degraded"
        return ExecutionHealth(
            status=overall,
            components=components,
            active_missions_count=self.queue.count_running() if self.queue else 0,
            queued_tasks_count=self.queue.count_queued() if self.queue else 0,
        )
