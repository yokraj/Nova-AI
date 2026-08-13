"""Desktop Recorder capturing window focus and UI automation control events.
"""

from typing import Optional
from app.ai.workflow_studio.models import RecordedEvent


class DesktopRecorder:
    """Captures active desktop window focus and native UI control events."""

    def capture_window_focus(self, window_title: str, app_name: str) -> RecordedEvent:
        """Captures window focus event."""
        return RecordedEvent(
            event_type="window_focus",
            target_app=app_name,
            target_control=window_title,
        )
