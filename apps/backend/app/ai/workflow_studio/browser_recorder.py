"""Browser Recorder capturing DOM navigation, tab switches, and web form interactions.
"""

from app.ai.workflow_studio.models import RecordedEvent


class BrowserRecorder:
    """Captures web browser navigation, tab events, and DOM element interactions."""

    def capture_navigation(self, url: str, tab_title: str) -> RecordedEvent:
        """Captures page navigation event."""
        return RecordedEvent(
            event_type="browser_navigate",
            target_app="Chrome",
            target_control=url,
            text_value=tab_title,
        )
