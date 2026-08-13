"""Copilot Manager administrative facade for AI Software Copilot.
"""

from typing import Any, Dict, Optional
from app.ai.copilot.configuration import CopilotConfiguration
from app.ai.copilot.interfaces import ICopilotManager
from app.ai.copilot.models import CopilotHealth, CopilotState


class CopilotManager(ICopilotManager):
    """High-level Copilot Manager controlling copilot lifecycle, configuration, and state transitions."""

    def __init__(self, config: Optional[CopilotConfiguration] = None) -> None:
        self.config = config or CopilotConfiguration()
        self._state = CopilotState.IDLE
        self._is_paused = False

    @property
    def state(self) -> CopilotState:
        """Returns current copilot state."""
        return self._state

    @property
    def is_paused(self) -> bool:
        """Returns True if copilot is currently paused."""
        return self._is_paused

    async def start(self) -> None:
        """Starts copilot engine."""
        self._state = CopilotState.IDLE
        self._is_paused = False

    async def pause(self) -> None:
        """Pauses copilot processing."""
        self._is_paused = True
        self._state = CopilotState.PAUSED

    async def resume(self) -> None:
        """Resumes copilot processing."""
        self._is_paused = False
        self._state = CopilotState.IDLE
