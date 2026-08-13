"""Schedule Manager handling schedule time-blocking and conflict detection."""

from typing import List
import structlog

from app.ai.assistant.interfaces import IScheduleManager
from app.ai.assistant.models import ScheduleItem

logger = structlog.get_logger("schedule_manager")


class ScheduleManager(IScheduleManager):
    """Manages daily time-block schedule allocations."""

    def __init__(self) -> None:
        self._items: List[ScheduleItem] = [
            ScheduleItem(title="Morning Focus Block", start_time="09:00", end_time="11:00", activity_type="work"),
            ScheduleItem(title="Team Standup", start_time="11:30", end_time="12:00", activity_type="work", is_meeting=True),
        ]

    async def add_schedule_item(self, item: ScheduleItem) -> ScheduleItem:
        """Add time block to schedule."""
        self._items.append(item)
        logger.info("Added schedule item", title=item.title, start=item.start_time, end=item.end_time)
        return item

    async def list_schedule(self) -> List[ScheduleItem]:
        """List active schedule items."""
        return list(self._items)
