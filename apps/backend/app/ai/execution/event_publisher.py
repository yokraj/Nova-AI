"""Execution Event Publisher broadcasting lifecycle events to subscribers."""

from typing import Any, Callable, Dict, List
import structlog

logger = structlog.get_logger("execution_event_publisher")


class ExecutionEventPublisher:
    """Emits mission and step lifecycle events."""

    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Subscribe to an event type (e.g. mission_started, step_completed)."""
        handlers = self._subscribers.setdefault(event_type, [])
        if handler not in handlers:
            handlers.append(handler)

    def publish(self, event_type: str, data: Dict[str, Any]) -> None:
        """Publish event to subscribers."""
        handlers = self._subscribers.get(event_type, [])
        logger.debug("Publishing execution event", event_type=event_type, count=len(handlers))
        for handler in handlers:
            try:
                handler(data)
            except Exception as err:
                logger.error("Error in execution event subscriber", event_type=event_type, error=str(err))
