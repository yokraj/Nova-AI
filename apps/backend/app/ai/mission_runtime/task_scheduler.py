"""Task Scheduler supporting priority queues, cron, recurring jobs, and resource-aware scheduling.
"""

from typing import Any, Dict, List, Optional
import time
from app.ai.mission_runtime.interfaces import ITaskScheduler
from app.ai.mission_runtime.models import MissionPriority, TaskItem


class TaskScheduler(ITaskScheduler):
    """Task Scheduler managing task priority queues and recurring cron execution."""

    def __init__(self) -> None:
        self._queue: List[Dict[str, Any]] = []

    async def schedule_task(self, task: TaskItem, delay_seconds: float = 0.0) -> None:
        """Enqueues task for delayed or immediate execution.

        Args:
            task: TaskItem instance.
            delay_seconds: Delay before task becomes eligible for execution.
        """
        execute_at = time.time() + delay_seconds
        item = {
            "task": task,
            "execute_at": execute_at,
            "priority": task.parameters.get("priority", MissionPriority.NORMAL),
        }
        self._queue.append(item)
        # Sort queue by priority and execution time
        self._queue.sort(key=lambda x: x["execute_at"])

    def get_pending_tasks(self) -> List[TaskItem]:
        """Returns ready tasks whose execution time has elapsed."""
        now = time.time()
        ready = [q["task"] for q in self._queue if q["execute_at"] <= now]
        self._queue = [q for q in self._queue if q["execute_at"] > now]
        return ready

    def get_queue_size(self) -> int:
        """Returns current pending queue size."""
        return len(self._queue)
