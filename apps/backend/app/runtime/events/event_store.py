"""EventStore capturing and listing historical SystemEvents.
"""

from datetime import datetime, UTC
from typing import List, Optional
from app.runtime.events.event import SystemEvent
from app.runtime.events.topics import Topic


class EventStore:
    """An in-memory event store capturing historical system events for replay/observability."""

    def __init__(self) -> None:
        """Initializes EventStore."""
        self._events: List[SystemEvent] = []

    def append(self, event: SystemEvent) -> None:
        """Appends a SystemEvent to the persistent history.

        Args:
            event: SystemEvent to store.
        """
        self._events.append(event)

    def list(self, topic: Optional[Topic] = None) -> List[SystemEvent]:
        """Lists stored system events.

        Args:
            topic: Optional topic filter.

        Returns:
            Filtered list of SystemEvent history records.
        """
        if topic is None:
            return list(self._events)
        return [e for e in self._events if e.topic == topic]

    def replay(self, topic: Optional[Topic] = None, since: Optional[datetime] = None) -> List[SystemEvent]:
        """Replays historical events matching topic and starting from since timestamp.

        Args:
            topic: Optional topic filter.
            since: Optional starting timestamp limit.

        Returns:
            Sorted chronological list of matching SystemEvents.
        """
        events = self.list(topic)
        if since is not None:
            since_utc = since if since.tzinfo else since.replace(tzinfo=UTC)
            events = [
                e
                for e in events
                if (e.timestamp.replace(tzinfo=UTC) if e.timestamp.tzinfo else e.timestamp) >= since_utc
            ]
        # Sort chronologically by timestamp
        events.sort(key=lambda e: e.timestamp)
        return events

    def purge(self) -> None:
        """Clears all historical events from the store."""
        self._events.clear()
