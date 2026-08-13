"""Session Manager tracking active authenticated site sessions."""

from typing import Dict
import structlog

logger = structlog.get_logger("session_manager")


class SessionManager:
    """Manages active authenticated browser session state across service portals."""

    def __init__(self) -> None:
        self._active_sessions: Dict[str, bool] = {}

    async def is_authenticated(self, service_id: str) -> bool:
        """Check if active session is authenticated."""
        return self._active_sessions.get(service_id, False)

    async def mark_authenticated(self, service_id: str, authenticated: bool = True) -> None:
        """Update authenticated session state."""
        self._active_sessions[service_id] = authenticated
        logger.info("Updated service session authentication state", service_id=service_id, auth=authenticated)
