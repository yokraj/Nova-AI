"""Preference Manager tracking user interaction preferences and habits."""

from typing import Any, Dict
import structlog

from app.ai.assistant.personal_memory import PersonalMemory

logger = structlog.get_logger("preference_manager")


class PreferenceManager:
    """Manages user preferences for work hours, app usage, and voice style."""

    def __init__(self) -> None:
        self.memory = PersonalMemory()

    async def get_preferences(self) -> Dict[str, Any]:
        """Get user preferences dictionary."""
        return {
            "work_hours": await self.memory.get_fact("work_hours"),
            "preferred_communication": await self.memory.get_fact("preferred_communication"),
            "favorite_apps": await self.memory.get_fact("favorite_apps"),
        }
