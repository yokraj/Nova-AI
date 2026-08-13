"""Skill Manager administrative facade for Skills Marketplace & SDK platform.
"""

from typing import Optional
from app.ai.skills.configuration import SkillConfiguration
from app.ai.skills.interfaces import ISkillManager


class SkillManager(ISkillManager):
    """High-level administrative manager for skill platform configuration and lifecycle."""

    def __init__(self, config: Optional[SkillConfiguration] = None) -> None:
        self.config = config or SkillConfiguration()
        self._is_active = True

    @property
    def is_active(self) -> bool:
        """Returns True if skill engine manager is active."""
        return self._is_active

    async def start(self) -> None:
        """Starts skill manager."""
        self._is_active = True
