"""Goal Manager tracking short-term and long-term personal/professional goals."""

from typing import List
import structlog

from app.ai.assistant.interfaces import IGoalManager
from app.ai.assistant.models import GoalItem, Timeframe

logger = structlog.get_logger("goal_manager")


class GoalManager(IGoalManager):
    """Tracks goals, milestones, and percentage progress."""

    def __init__(self) -> None:
        self._goals: List[GoalItem] = [
            GoalItem(title="Release Nova AI OS v1.0", timeframe=Timeframe.MONTHLY, progress_percentage=85.0),
        ]

    async def add_goal(self, title: str, timeframe: str = "monthly") -> GoalItem:
        """Add new goal."""
        tf = Timeframe(timeframe) if timeframe in [t.value for t in Timeframe] else Timeframe.MONTHLY
        goal = GoalItem(title=title, timeframe=tf)
        self._goals.append(goal)
        logger.info("Added goal", title=title, timeframe=timeframe)
        return goal

    async def update_goal_progress(self, goal_id: str, progress: float) -> GoalItem:
        """Update progress percentage."""
        goal = next((g for g in self._goals if g.goal_id == goal_id), self._goals[0])
        goal.progress_percentage = progress
        if progress >= 100.0:
            goal.completed = True
        logger.info("Updated goal progress", id=goal_id, progress=progress)
        return goal

    async def list_goals(self) -> List[GoalItem]:
        """List active goals."""
        return list(self._goals)
