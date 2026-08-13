"""Subsystem Manager facade for Workspace platform configuration and lifecycle.
"""

from typing import Optional
from app.ai.workspace.configuration import WorkspaceConfiguration
from app.ai.workspace.interfaces import IWorkspaceManagerFacade


class WorkspaceManagerFacade(IWorkspaceManagerFacade):
    """High-level administrative manager for workspace platform configuration and lifecycle."""

    def __init__(self, config: Optional[WorkspaceConfiguration] = None) -> None:
        self.config = config or WorkspaceConfiguration()
        self._is_active = True

    @property
    def is_active(self) -> bool:
        """Returns True if workspace manager facade is active."""
        return self._is_active

    async def start(self) -> None:
        """Starts workspace manager."""
        self._is_active = True
