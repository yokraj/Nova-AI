"""Workspace Manager creating, loading, and managing Personal, Developer, Research, Organization, Education, and Enterprise Workspaces.
"""

from typing import List, Optional
from app.ai.workspace.interfaces import IWorkspaceManager
from app.ai.workspace.models import WorkspaceDefinition, WorkspaceType


class WorkspaceManager(IWorkspaceManager):
    """Manages workspace lifecycle across Personal, Team, Organization, and Enterprise workspaces."""

    def __init__(self) -> None:
        self._workspaces: List[WorkspaceDefinition] = []

    def create_workspace(self, name: str, workspace_type: str = "personal") -> WorkspaceDefinition:
        """Creates new workspace definition.

        Args:
            name: Workspace name.
            workspace_type: WorkspaceType string.

        Returns:
            WorkspaceDefinition instance.
        """
        wtype = WorkspaceType.PERSONAL
        try:
            wtype = WorkspaceType(workspace_type.lower())
        except ValueError:
            pass

        ws = WorkspaceDefinition(name=name, workspace_type=wtype)
        self._workspaces.append(ws)
        return ws
