"""Task Manager handling personal and work task tracking."""

from typing import List
import structlog

from app.ai.assistant.interfaces import ITaskManager
from app.ai.assistant.models import TaskItem

logger = structlog.get_logger("task_manager")


class TaskManager(ITaskManager):
    """Manages task items, status updates, and priority sorting."""

    def __init__(self) -> None:
        self._tasks: List[TaskItem] = [
            TaskItem(title="Complete Nova AI Specs", category="work", priority=1),
            TaskItem(title="Schedule gym session", category="health", priority=2),
        ]

    async def add_task(self, title: str, category: str = "work", priority: int = 1) -> TaskItem:
        """Add new task."""
        item = TaskItem(title=title, category=category, priority=priority)
        self._tasks.append(item)
        logger.info("Added task", title=title, category=category)
        return item

    async def list_tasks(self, completed: bool = False) -> List[TaskItem]:
        """List tasks."""
        return [t for t in self._tasks if t.completed == completed]
