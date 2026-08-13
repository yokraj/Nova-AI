"""Event Stream real-time recorded event buffer and event listener publisher.
"""

from typing import List
from app.ai.workflow_studio.models import RecordedEvent


class EventStream:
    """Manages real-time event stream buffering and listener dispatching."""

    def __init__(self) -> None:
        self._buffer: List[RecordedEvent] = []

    def push_event(self, event: RecordedEvent) -> None:
        """Pushes event to real-time stream."""
        self._buffer.append(event)

    def get_stream_buffer(self) -> List[RecordedEvent]:
        """Returns snapshot of current stream buffer."""
        return list(self._buffer)
