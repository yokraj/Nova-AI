"""Subsystem Manager facade for Workflow Studio platform configuration and lifecycle.
"""

from typing import Optional
from app.ai.workflow_studio.configuration import WorkflowStudioConfiguration
from app.ai.workflow_studio.interfaces import IWorkflowStudioManager


class WorkflowStudioManager(IWorkflowStudioManager):
    """High-level administrative manager for workflow studio platform configuration and lifecycle."""

    def __init__(self, config: Optional[WorkflowStudioConfiguration] = None) -> None:
        self.config = config or WorkflowStudioConfiguration()
        self._is_active = True

    @property
    def is_active(self) -> bool:
        """Returns True if workflow studio manager is active."""
        return self._is_active

    async def start(self) -> None:
        """Starts workflow studio manager."""
        self._is_active = True
