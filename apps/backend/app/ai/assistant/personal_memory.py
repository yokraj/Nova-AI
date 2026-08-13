"""Personal Memory storing long-term personal facts, past decisions, and life preferences."""

from typing import Any, Dict, Optional
import structlog

logger = structlog.get_logger("personal_memory")


class PersonalMemory:
    """Stores long-term personal facts, user history, and past decisions."""

    def __init__(self) -> None:
        self._memory: Dict[str, Any] = {
            "work_hours": "09:00 - 18:00",
            "preferred_communication": "concise voice summary",
            "gym_time": "18:30",
            "favorite_apps": ["VS Code", "Chrome", "Notepad"],
        }

    async def get_fact(self, key: str, default: Optional[Any] = None) -> Any:
        """Get personal fact."""
        return self._memory.get(key, default)

    async def remember_fact(self, key: str, value: Any) -> None:
        """Remember personal fact."""
        self._memory[key] = value
        logger.info("Saved personal memory fact", key=key, value=value)
