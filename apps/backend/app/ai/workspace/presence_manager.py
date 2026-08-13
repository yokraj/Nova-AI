"""Presence Manager tracking real-time active member presence, typing indicators, and focus.
"""

from typing import Any, Dict, List


class PresenceManager:
    """Tracks active online members, typing indicators, and active application focus across nodes."""

    def get_online_members(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Returns list of currently online workspace members."""
        return [
            {"email": "lead@corp.org", "status": "active", "focused_app": "VS Code"},
            {"email": "dev@corp.org", "status": "active", "focused_app": "Chrome"},
        ]
