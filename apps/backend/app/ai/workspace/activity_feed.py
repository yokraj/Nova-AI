"""Activity Feed tracking real-time workspace audit events and activity history.
"""

from typing import Any, Dict, List


class ActivityFeed:
    """Records and serves real-time workspace activity audit log events."""

    def __init__(self) -> None:
        self._feed: List[Dict[str, Any]] = []

    def record_activity(self, workspace_id: str, actor: str, action: str) -> None:
        """Records activity log entry."""
        self._feed.append({
            "workspace_id": workspace_id,
            "actor": actor,
            "action": action,
        })

    def get_activities(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Returns activities list for workspace_id."""
        return [a for a in self._feed if a["workspace_id"] == workspace_id] or [
            {"workspace_id": workspace_id, "actor": "system", "action": "Workspace initialized"}
        ]
