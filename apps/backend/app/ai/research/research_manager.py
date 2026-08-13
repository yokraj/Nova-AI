"""Research Manager administrative facade for Knowledge, Research & Reasoning Engine.
"""

from typing import Optional
from app.ai.research.configuration import ResearchConfiguration
from app.ai.research.interfaces import IResearchManager


class ResearchManager(IResearchManager):
    """High-level administrative manager for research configuration and engine lifecycle."""

    def __init__(self, config: Optional[ResearchConfiguration] = None) -> None:
        self.config = config or ResearchConfiguration()
        self._is_active = True

    @property
    def is_active(self) -> bool:
        """Returns True if research engine is active."""
        return self._is_active

    async def start(self) -> None:
        """Starts research engine manager."""
        self._is_active = True
