"""Shared Skills library for team skill discovery and installation.
"""

from typing import Any, Dict, List


class SharedSkills:
    """Manages shared workspace skills library across team members."""

    def list_team_skills(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Returns list of shared skills available in workspace."""
        return [
            {"skill_id": "skill_vscode", "name": "VS Code IDE Skill", "installed_by": "lead@corp.org"},
            {"skill_id": "skill_docker", "name": "Docker Container Skill", "installed_by": "dev@corp.org"},
        ]
