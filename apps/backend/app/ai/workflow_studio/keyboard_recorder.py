"""Keyboard Recorder capturing keystrokes and hotkey shortcuts.
"""

from app.ai.workflow_studio.models import RecordedEvent


class KeyboardRecorder:
    """Captures keyboard input events, text typing, and key combinations."""

    def capture_typing(self, text: str, app_name: str = "VSCode") -> RecordedEvent:
        """Captures text typing event."""
        return RecordedEvent(
            event_type="type_text",
            target_app=app_name,
            text_value=text,
        )
