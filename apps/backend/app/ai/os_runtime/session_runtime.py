"""Session Runtime managing multi-conversation, multi-workflow, and multi-workspace sessions.
"""

from typing import Any, Dict
from app.ai.os_runtime.models import OSSession


class SessionRuntime:
    """Manages active AI OS user sessions, desktop state persistence, and multi-workspace switching."""

    def __init__(self) -> None:
        self._active_session = OSSession(
            user_id="owner@nova-ai.org",
            active_workspace="Nova Enterprise Core",
            active_desktop="Desktop 1",
        )

    async def get_active_session(self) -> OSSession:
        """Returns active AI OS session snapshot."""
        return self._active_session

    async def switch_workspace(self, workspace_name: str) -> OSSession:
        """Switches active workspace context in current OS session."""
        self._active_session.active_workspace = workspace_name
        return self._active_session
