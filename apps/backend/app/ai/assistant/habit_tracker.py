"""Habit Tracker tracking habit streaks and daily completion."""

from typing import List
import structlog

from app.ai.assistant.models import HabitRecord

logger = structlog.get_logger("habit_tracker")


class HabitTracker:
    """Tracks habit streaks and logs completions."""

    def __init__(self) -> None:
        self._habits: List[HabitRecord] = [
            HabitRecord(name="Gym Workout", streak_count=7),
            HabitRecord(name="Read 20 pages", streak_count=12),
        ]

    async def log_habit(self, habit_name: str) -> HabitRecord:
        """Log habit completion."""
        habit = next((h for h in self._habits if h.name.lower() == habit_name.lower()), None)
        if not habit:
            habit = HabitRecord(name=habit_name, streak_count=1)
            self._habits.append(habit)
        else:
            habit.streak_count += 1

        logger.info("Logged habit completion", name=habit.name, streak=habit.streak_count)
        return habit

    async def list_habits(self) -> List[HabitRecord]:
        """List active habits."""
        return list(self._habits)
