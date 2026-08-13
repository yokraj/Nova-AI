"""Central Event Bus for AI OS Kernel pub-sub messaging.
"""

import asyncio
from typing import Any, Callable, Dict, List
from app.ai.kernel.interfaces import IEventBus
from app.ai.kernel.models import EventRecord


class EventBus(IEventBus):
    """Asynchronous central event bus."""

    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Callable[[EventRecord], Any]]] = {}
        self._history: List[EventRecord] = []

    async def publish(self, event_type: str, payload: Dict[str, Any], source: str = "kernel") -> EventRecord:
        """Publishes an event to all subscribers.

        Args:
            event_type: Event type name (e.g. MISSION_STARTED).
            payload: Event data dictionary.
            source: Source identifier.

        Returns:
            EventRecord instance.
        """
        event = EventRecord(event_type=event_type, payload=payload, source=source)
        self._history.append(event)

        callbacks = self._subscribers.get(event_type, [])
        callbacks.extend(self._subscribers.get("*", []))

        for cb in callbacks:
            try:
                res = cb(event)
                if asyncio.iscoroutine(res):
                    await res
            except Exception:
                pass

        return event

    def subscribe(self, event_type: str, callback: Callable[[EventRecord], Any]) -> None:
        """Subscribes callback to an event type.

        Args:
            event_type: Event type string or '*' for all events.
            callback: Function to invoke on event publish.
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def event_history(self, limit: int = 50) -> List[EventRecord]:
        """Returns recent event history records."""
        return self._history[-limit:]
