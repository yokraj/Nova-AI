"""Routine Manager managing morning/evening routines and trigger sequences."""

from typing import List
import structlog

from app.ai.assistant.models import RoutineDefinition

logger = structlog.get_logger("routine_manager")


class RoutineManager:
    """Manages morning/evening routine definitions and automated action triggers."""

    def __init__(self) -> None:
        self._routines: List[RoutineDefinition] = [
            RoutineDefinition(routine_id="morning_rtn", name="Morning Kickstart", time_of_day="morning", actions=["Morning Briefing", "Calendar Review", "Hydration Check"]),
            RoutineDefinition(routine_id="evening_rtn", name="Evening Wind-down", time_of_day="evening", actions=["Daily Recap", "Task Priority Sync", "Tomorrow Planning"]),
        ]

    async def execute_routine(self, routine_id: str) -> RoutineDefinition:
        """Execute routine sequence."""
        rtn = next((r for r in self._routines if r.routine_id == routine_id), self._routines[0])
        logger.info("Executing routine sequence", name=rtn.name, actions_count=len(rtn.actions))
        return rtn

    async def list_routines(self) -> List[RoutineDefinition]:
        """List active routines."""
        return list(self._routines)
