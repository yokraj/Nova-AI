"""Subsystem Manager facade for Self-Improvement & Adaptive Intelligence platform.
"""

from typing import Optional
from app.ai.self_improvement.configuration import SelfImprovementConfiguration
from app.ai.self_improvement.interfaces import ISelfImprovementManager


class SelfImprovementManager(ISelfImprovementManager):
    """High-level administrative manager for self-improvement platform configuration and lifecycle."""

    def __init__(self, config: Optional[SelfImprovementConfiguration] = None) -> None:
        self.config = config or SelfImprovementConfiguration()
        self._is_active = True

    @property
    def is_active(self) -> bool:
        """Returns True if self-improvement engine manager is active."""
        return self._is_active

    async def start(self) -> None:
        """Starts self-improvement manager."""
        self._is_active = True
