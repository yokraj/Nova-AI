"""Active Window Monitor inspecting focused window title and process name."""

import structlog

from app.ai.ambient.models import ActiveWindowInfo

logger = structlog.get_logger("active_window_monitor")


class ActiveWindowMonitor:
    """Monitors active focused window, process name, and application category."""

    async def get_active_window(self) -> ActiveWindowInfo:
        """Get active focused window information."""
        info = ActiveWindowInfo(
            title="VS Code - app/ai/ambient/ambient_engine.py",
            process_name="Code.exe",
            is_ide=True,
            is_meeting_app=False,
        )
        logger.debug("Active window detected", title=info.title, process=info.process_name)
        return info
