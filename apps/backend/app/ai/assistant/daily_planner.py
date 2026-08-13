"""Daily Planner generating morning briefings, schedule time-blocks, and evening summaries."""

from datetime import datetime
from typing import List
import structlog

from app.ai.assistant.interfaces import IDailyPlanner
from app.ai.assistant.models import DailyPlan, ReminderItem, ScheduleItem, TaskItem

logger = structlog.get_logger("daily_planner")


class DailyPlanner(IDailyPlanner):
    """Generates daily life plans, morning briefings, schedule allocations, and evening summaries."""

    async def generate_morning_briefing(self) -> DailyPlan:
        """Generate morning briefing and day plan."""
        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        briefing = (
            f"Good morning! Today is {today_str}. You have 2 meetings scheduled, "
            "3 high-priority tasks, and 1 goal milestone due this evening."
        )

        schedule = [
            ScheduleItem(title="Morning Routine & Workout", start_time="07:30", end_time="08:30", activity_type="health"),
            ScheduleItem(title="Sprint Planning Meeting", start_time="10:00", end_time="11:00", activity_type="work", is_meeting=True),
            ScheduleItem(title="Deep Work: Nova AI Engine", start_time="11:30", end_time="13:30", activity_type="work"),
            ScheduleItem(title="Architecture Review Meeting", start_time="15:00", end_time="16:00", activity_type="work", is_meeting=True),
        ]

        top_tasks = [
            TaskItem(title="Pay electricity bill", category="finance", priority=1),
            TaskItem(title="Review backend PRs", category="work", priority=2),
            TaskItem(title="Gym workout", category="health", priority=2),
        ]

        reminders = [
            ReminderItem(title="Pay electricity bill tomorrow", due_time="18:00"),
        ]

        logger.info("Generated morning briefing plan", date=today_str)
        return DailyPlan(
            plan_date=today_str,
            morning_briefing=briefing,
            schedule=schedule,
            top_tasks=top_tasks,
            reminders=reminders,
        )

    async def generate_evening_summary(self) -> str:
        """Generate evening recap and daily summary."""
        summary = (
            "Evening Recap: Today you completed 3 out of 3 focus tasks, attended 2 meetings, "
            "and maintained your 7-day workout streak. Great work!"
        )
        logger.info("Generated evening summary")
        return summary
