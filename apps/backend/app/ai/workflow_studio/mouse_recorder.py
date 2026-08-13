"""Mouse Recorder capturing mouse clicks, double clicks, scrolls, and drag actions.
"""

from app.ai.workflow_studio.models import RecordedEvent


class MouseRecorder:
    """Captures mouse clicks, coordinates, and drag-and-drop actions."""

    def capture_click(self, x: int, y: int, control_name: str, app_name: str = "Desktop") -> RecordedEvent:
        """Captures mouse click event."""
        return RecordedEvent(
            event_type="click",
            target_app=app_name,
            target_control=control_name,
            x=x,
            y=y,
        )
