"""Shared Plugins registry for team plugin distribution.
"""

from typing import Any, Dict, List


class SharedPlugins:
    """Manages shared workspace plugin registry."""

    def list_team_plugins(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Returns list of shared plugins in workspace."""
        return [
            {"plugin_id": "plugin_git_integration", "name": "Git Enterprise Plugin"},
        ]
