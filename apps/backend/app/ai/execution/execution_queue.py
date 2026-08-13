"""Prioritized FIFO Execution Queue supporting concurrent execution and cancellation."""

import anyio
from typing import Dict, List, Optional
import structlog

from app.ai.execution.models import MissionExecutionPlan, PriorityLevel

logger = structlog.get_logger("execution_queue")


class ExecutionQueue:
    """Thread-safe prioritized queue managing mission plans."""

    def __init__(self, max_concurrent: int = 5) -> None:
        self.max_concurrent = max_concurrent
        self._queue: List[MissionExecutionPlan] = []
        self._running: Dict[str, MissionExecutionPlan] = {}

    def enqueue(self, plan: MissionExecutionPlan) -> None:
        """Add a mission plan to the queue, ordered by priority descending."""
        self._queue.append(plan)
        self._queue.sort(key=lambda p: p.priority.value, reverse=True)
        logger.info("Enqueued mission plan", mission_id=plan.mission_id, priority=plan.priority.name)

    def dequeue(self) -> Optional[MissionExecutionPlan]:
        """Pop highest-priority mission plan from queue if under max concurrency."""
        if len(self._running) >= self.max_concurrent or not self._queue:
            return None
        plan = self._queue.pop(0)
        self._running[plan.mission_id] = plan
        return plan

    def mark_completed(self, mission_id: str) -> None:
        """Remove completed mission from running set."""
        self._running.pop(mission_id, None)

    def cancel(self, mission_id: str) -> bool:
        """Cancel queued or running mission."""
        # Remove from queue
        self._queue = [p for p in self._queue if p.mission_id != mission_id]
        running_plan = self._running.pop(mission_id, None)
        if running_plan:
            running_plan.state = running_plan.state.CANCELLED
            logger.info("Cancelled running mission", mission_id=mission_id)
            return True
        return False

    def list_queued(self) -> List[MissionExecutionPlan]:
        """Return list of queued missions."""
        return list(self._queue)

    def list_running(self) -> List[MissionExecutionPlan]:
        """Return list of active running missions."""
        return list(self._running.values())

    def count_queued(self) -> int:
        return len(self._queue)

    def count_running(self) -> int:
        return len(self._running)
