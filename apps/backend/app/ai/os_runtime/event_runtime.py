"""Global Event Runtime serving as the central pub-sub event bus for all 25 Nova subsystems.
"""

from typing import Any, Callable, Dict, List
from app.ai.os_runtime.models import SystemEvent


class GlobalEventRuntime:
    """Central OS Event Bus allowing all subsystems and agents to publish and subscribe to real-time system events."""

    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Callable[[SystemEvent], Any]]] = {}
        self._event_history: List[SystemEvent] = []

    async def publish_event(self, event_type: str, payload: Dict[str, Any], source: str = "os_kernel") -> SystemEvent:
        """Publishes system event across global OS bus."""
        event = SystemEvent(event_type=event_type, source=source, payload=payload)
        self._event_history.append(event)

        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(event)
                except Exception:
                    pass
        return event

    def subscribe(self, event_type: str, callback_fn: Callable[[SystemEvent], Any]) -> None:
        """Subscribes callback function to event topic."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback_fn)

    def get_event_history(self) -> List[SystemEvent]:
        """Returns log of published system events."""
        return list(self._event_history)
