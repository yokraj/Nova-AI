"""Plugin Event Manager publishing plugin lifecycle and execution events."""

from typing import Any, Callable, Dict, List
import structlog

logger = structlog.get_logger("plugin_event_manager")


class PluginEventManager:
    """Publishes plugin events to registered subscribers."""

    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Subscribe to a specific event type (e.g. plugin_loaded, plugin_executed)."""
        handlers = self._subscribers.setdefault(event_type, [])
        if handler not in handlers:
            handlers.append(handler)

    def publish(self, event_type: str, data: Dict[str, Any]) -> None:
        """Publish event data to subscribers."""
        handlers = self._subscribers.get(event_type, [])
        logger.debug("Publishing event", event_type=event_type, subscribers=len(handlers))
        for handler in handlers:
            try:
                handler(data)
            except Exception as err:
                logger.error("Event handler error", event_type=event_type, error=str(err))
