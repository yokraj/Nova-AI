"""Abstract interface contracts for Autonomous Personal Assistant & Life Management Engine."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.ai.assistant.models import (
    AssistantHealth,
    AssistantMetrics,
    DailyPlan,
    GoalItem,
    MeetingRecord,
    ReminderItem,
    ScheduleItem,
    TaskItem,
)


class IDailyPlanner(ABC):
    """Abstract contract for daily planning and briefings."""

    @abstractmethod
    async def generate_morning_briefing(self) -> DailyPlan:
        pass

    @abstractmethod
    async def generate_evening_summary(self) -> str:
        pass


class IScheduleManager(ABC):
    """Abstract contract for calendar schedule management."""

    @abstractmethod
    async def add_schedule_item(self, item: ScheduleItem) -> ScheduleItem:
        pass

    @abstractmethod
    async def list_schedule(self) -> List[ScheduleItem]:
        pass


class IReminderManager(ABC):
    """Abstract contract for reminder creation and dispatching."""

    @abstractmethod
    async def create_reminder(self, title: str, due_time: str) -> ReminderItem:
        pass

    @abstractmethod
    async def list_reminders(self) -> List[ReminderItem]:
        pass


class ITaskManager(ABC):
    """Abstract contract for personal task management."""

    @abstractmethod
    async def add_task(self, title: str, category: str = "work", priority: int = 1) -> TaskItem:
        pass

    @abstractmethod
    async def list_tasks(self, completed: bool = False) -> List[TaskItem]:
        pass


class IGoalManager(ABC):
    """Abstract contract for long-term goal tracking."""

    @abstractmethod
    async def add_goal(self, title: str, timeframe: str = "monthly") -> GoalItem:
        pass

    @abstractmethod
    async def update_goal_progress(self, goal_id: str, progress: float) -> GoalItem:
        pass


class IRecommendationEngine(ABC):
    """Abstract contract for proactive suggestions."""

    @abstractmethod
    async def get_proactive_recommendations(self) -> List[str]:
        pass


class IPersonalAssistantPlatform(ABC):
    """Abstract contract for central Personal Assistant Platform facade."""

    @abstractmethod
    async def process_voice_query(self, query: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def get_metrics(self) -> AssistantMetrics:
        pass

    @abstractmethod
    def check_health(self) -> AssistantHealth:
        pass
