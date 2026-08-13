"""Subsystem Manager facade for Desktop Automation Platform configuration and lifecycle.
"""

from typing import Optional
from app.ai.desktop_automation.configuration import DesktopAutomationConfiguration
from app.ai.desktop_automation.interfaces import IDesktopAutomationManagerFacade


class DesktopAutomationManagerFacade(IDesktopAutomationManagerFacade):
    """High-level administrative manager for desktop automation configuration and lifecycle."""

    def __init__(self, config: Optional[DesktopAutomationConfiguration] = None) -> None:
        self.config = config or DesktopAutomationConfiguration()
        self._is_active = True

    @property
    def is_active(self) -> bool:
        """Returns True if desktop automation manager facade is active."""
        return self._is_active

    async def start(self) -> None:
        """Starts desktop automation manager."""
        self._is_active = True
