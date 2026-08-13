"""Priority Manager computing dynamic priority scores for tasks, goals, and meetings."""

from typing import List
import structlog

from app.ai.assistant.models import TaskItem

logger = structlog.get_logger("priority_manager")


class PriorityManager:
    """Computes dynamic priority scores based on due dates, deadlines, and project milestones."""

    async def sort_tasks_by_priority(self, tasks: List[TaskItem]) -> List[TaskItem]:
        """Sort tasks by priority score."""
        sorted_tasks = sorted(tasks, key=lambda t: t.priority)
        logger.debug("Sorted tasks by priority score", count=len(sorted_tasks))
        return sorted_tasks
