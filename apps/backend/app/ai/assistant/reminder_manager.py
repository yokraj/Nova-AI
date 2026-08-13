"""Reminder Manager handling time-based and context-based reminder creation and triggers."""

from typing import List
import structlog

from app.ai.assistant.interfaces import IReminderManager
from app.ai.assistant.models import ReminderItem, ReminderPriority

logger = structlog.get_logger("reminder_manager")


class ReminderManager(IReminderManager):
    """Manages reminder items and triggers."""

    def __init__(self) -> None:
        self._reminders: List[ReminderItem] = [
            ReminderItem(title="Pay electricity bill tomorrow", due_time="18:00", priority=ReminderPriority.HIGH),
        ]

    async def create_reminder(self, title: str, due_time: str) -> ReminderItem:
        """Create new reminder."""
        item = ReminderItem(title=title, due_time=due_time)
        self._reminders.append(item)
        logger.info("Created reminder", title=title, due_time=due_time)
        return item

    async def list_reminders(self) -> List[ReminderItem]:
        """List reminders."""
        return list(self._reminders)
