"""Asynchronous event dispatching system for Nova AI workflows.

Allows step status event callbacks subscriptions and domain event publishing.
"""

import asyncio
import inspect
from typing import Any, Callable, Dict, List

import structlog

logger = structlog.get_logger(__name__)


class EventBus:
    """Publish-Subscribe broker dispatching execution and state change events."""

    def __init__(self) -> None:
        self._listeners: Dict[str, List[Callable[[Any], Any]]] = {}

    def subscribe(
        self, event_type: str, callback: Callable[[Any], Any]
    ) -> None:
        """Subscribes a listener callback to an event type.

        Args:
            event_type: String representation of target event.
            callback: Function to invoke when event occurs.
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    async def publish(self, event_type: str, data: Any) -> None:
        """Publishes an event to all subscribed listeners.

        Args:
            event_type: Target event identifier name.
            data: Payload details dictionary/object sent to listeners.
        """
        if event_type not in self._listeners:
            return

        tasks = []
        for callback in self._listeners[event_type]:
            try:
                if inspect.iscoroutinefunction(callback):
                    tasks.append(callback(data))
                else:
                    callback(data)
            except Exception as error:
                logger.error(
                    "event_listener_execution_failed",
                    event_type=event_type,
                    error=str(error),
                )

        if tasks:
            # Execute async callbacks in parallel safely returning exceptions
            await asyncio.gather(*tasks, return_exceptions=True)
