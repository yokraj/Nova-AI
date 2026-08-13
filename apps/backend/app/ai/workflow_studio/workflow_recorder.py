"""Master Workflow Recorder orchestrating desktop, browser, keyboard, mouse, and voice recorders.
"""

from typing import List
from app.ai.workflow_studio.interfaces import IWorkflowRecorder
from app.ai.workflow_studio.models import RecordedEvent, WorkflowRecordingState


class WorkflowRecorder(IWorkflowRecorder):
    """Master workflow recorder capturing input events across applications."""

    def __init__(self) -> None:
        self.state = WorkflowRecordingState.IDLE
        self._recorded_events: List[RecordedEvent] = []

    def start_recording(self, session_name: str) -> str:
        """Starts recording session."""
        self.state = WorkflowRecordingState.RECORDING
        self._recorded_events.clear()
        return session_name

    def record_event(self, event: RecordedEvent) -> None:
        """Appends event to recording buffer if state is RECORDING."""
        if self.state == WorkflowRecordingState.RECORDING:
            self._recorded_events.append(event)

    def stop_recording(self) -> List[RecordedEvent]:
        """Stops recording session and returns recorded events."""
        self.state = WorkflowRecordingState.STOPPED
        return list(self._recorded_events)
