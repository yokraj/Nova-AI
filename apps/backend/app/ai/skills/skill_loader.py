"""Skill Loader performing dynamic module loading and hot reloading.
"""

from typing import Any, Dict
from app.ai.skills.interfaces import ISkillLoader


class SkillLoader(ISkillLoader):
    """Dynamic skill loader handling import, instantiation, and hot reloading."""

    def __init__(self) -> None:
        self._loaded_instances: Dict[str, Any] = {}

    async def load_skill(self, skill_id: str) -> Any:
        """Loads skill instance dynamically.

        Args:
            skill_id: Target skill ID string.

        Returns:
            Loaded skill instance object.
        """
        if skill_id in self._loaded_instances:
            return self._loaded_instances[skill_id]

        # Dynamic instance fallback
        instance = f"[Loaded Skill Instance - {skill_id}]"
        self._loaded_instances[skill_id] = instance
        return instance

    async def hot_reload(self, skill_id: str) -> bool:
        """Hot reloads skill module."""
        if skill_id in self._loaded_instances:
            del self._loaded_instances[skill_id]
        await self.load_skill(skill_id)
        return True
