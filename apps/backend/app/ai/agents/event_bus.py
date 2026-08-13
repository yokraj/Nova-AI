"""Event Bus broker supporting async Pub/Sub event distribution.
"""

import asyncio
import structlog
from typing import Any, Callable, Coroutine, Dict, List

logger = structlog.get_logger("event_bus")

class EventBus:
    """Asynchronous dispatcher facilitating communications via trigger events."""

    def __init__(self) -> None:
        self._listeners: Dict[str, List[Callable[..., Coroutine[Any, Any, None]]]] = {}

    def subscribe(self, event_type: str, callback: Callable[..., Coroutine[Any, Any, None]]) -> None:
        """Subscribes an async callback to target event names."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        if callback not in self._listeners[event_type]:
            self._listeners[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable[..., Coroutine[Any, Any, None]]) -> None:
        """Removes registered callback from target event."""
        if event_type in self._listeners and callback in self._listeners[event_type]:
            self._listeners[event_type].remove(callback)

    async def publish(self, event_type: str, *args: Any, **kwargs: Any) -> None:
        """Fires target event type, invoking all subscribers concurrently."""
        listeners = self._listeners.get(event_type, [])
        if not listeners:
            return

        tasks = [asyncio.create_task(cb(*args, **kwargs)) for cb in listeners]
        # Resolve all tasks concurrently capturing failures safely
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for res in results:
            if isinstance(res, Exception):
                logger.error("Subscriber task failed on event", event_type=event_type, error=str(res))
        
        logger.debug("Broadcast event completed", event_name=event_type, listeners_count=len(listeners))
