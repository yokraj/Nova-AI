"""Context Pipeline unifying desktop window, clipboard, notification, and idle monitors."""

import structlog

from app.ai.ambient.active_window_monitor import ActiveWindowMonitor
from app.ai.ambient.application_monitor import ApplicationMonitor
from app.ai.ambient.clipboard_monitor import ClipboardMonitor
from app.ai.ambient.idle_detector import IdleDetector
from app.ai.ambient.models import DesktopContextSnapshot
from app.ai.ambient.notification_monitor import NotificationMonitor

logger = structlog.get_logger("context_pipeline")


class ContextPipeline:
    """Aggregates active window, clipboard, notifications, application state, and idle detector into unified snapshot."""

    def __init__(self) -> None:
        self.window_monitor = ActiveWindowMonitor()
        self.clipboard_monitor = ClipboardMonitor()
        self.notification_monitor = NotificationMonitor()
        self.app_monitor = ApplicationMonitor()
        self.idle_detector = IdleDetector()

    async def get_composite_snapshot(self) -> DesktopContextSnapshot:
        """Capture composite snapshot across all desktop context channels."""
        window = await self.window_monitor.get_active_window()
        clip = await self.clipboard_monitor.get_clipboard_snapshot()
        notifications = await self.notification_monitor.get_recent_notifications()
        in_meeting = await self.app_monitor.is_meeting_active()
        is_idle = await self.idle_detector.is_user_idle()

        snapshot = DesktopContextSnapshot(
            active_window=window,
            clipboard=clip,
            notifications=notifications,
            is_user_idle=is_idle,
            is_in_meeting=in_meeting,
            uncommitted_changes=True,
            debugging_duration_minutes=45.0,
        )
        logger.debug("Unified desktop context snapshot captured", process=window.process_name, meeting=in_meeting)
        return snapshot
