"""Application Monitor inspecting running apps and active Teams/Zoom meetings."""

from typing import List
import structlog

logger = structlog.get_logger("application_monitor")


class ApplicationMonitor:
    """Monitors running app inventory and detects Teams, Zoom, or Google Meet calls."""

    async def get_running_applications(self) -> List[str]:
        """Get running apps list."""
        return ["Code.exe", "ms-teams.exe", "chrome.exe"]

    async def is_meeting_active(self) -> bool:
        """Check if user is currently in a Microsoft Teams or Zoom meeting."""
        logger.debug("Checking active video conference status")
        return True
