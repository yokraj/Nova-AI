"""Shared Projects manager for SDLC code repositories across workspace teams.
"""

from typing import Any, Dict, List


class SharedProjects:
    """Manages shared SDLC project code repositories across team workspace members."""

    def list_projects(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Returns list of shared projects."""
        return [
            {"project_id": "proj_nova_ai", "name": "Nova-AI Monorepo", "path": "c:\\Projects\\Nova-AI"},
        ]
