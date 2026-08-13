"""Workspace Context tracking active members, projects, active tasks, and online devices.
"""

from typing import Any, Dict, List


class WorkspaceContext:
    """Tracks active workspace state including online members, open projects, and active tasks."""

    def get_workspace_snapshot(self, workspace_id: str) -> Dict[str, Any]:
        """Returns active workspace snapshot dictionary."""
        return {
            "workspace_id": workspace_id,
            "active_members_count": 4,
            "active_projects_count": 2,
            "active_tasks_count": 5,
        }
