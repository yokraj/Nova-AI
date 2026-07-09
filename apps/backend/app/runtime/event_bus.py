"""Runtime Event Bus subsystem for Nova AI.

Stores history logs, matches wildcard topics, and dispatches replayable events.
"""

import asyncio
import inspect
from typing import Any, Callable, Dict, List
import structlog

from app.runtime.interfaces import IKernelService
from app.runtime.types import RuntimeEvent

logger = structlog.get_logger(__name__)


class RuntimeEventBus(IKernelService):
    """Subsystem managing publish-subscribe event dispatching and history replay."""

    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Callable[[RuntimeEvent], Any]]] = {}
        self._history: List[RuntimeEvent] = []

    async def start(self) -> None:
        """Starts the Event Bus service."""
        logger.info("runtime_event_bus_started")

    async def stop(self) -> None:
        """Flushes event histories and subscribers."""
        self._subscribers.clear()
        self._history.clear()
        logger.info("runtime_event_bus_stopped")

    @property
    def name(self) -> str:
        """Unique service identifier."""
        return "event_bus"

    def subscribe(
        self, topic: str, callback: Callable[[RuntimeEvent], Any]
    ) -> None:
        """Registers a listener function to a topic.

        Args:
            topic: Target topic name or wildcard pattern (e.g. 'system.*').
            callback: Listener callback function.
        """
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(callback)
        logger.debug("event_topic_subscribed", topic=topic)

    async def publish(self, event: RuntimeEvent) -> None:
        """Saves event in history and dispatches it to subscribers.

        Args:
            event: The RuntimeEvent model to publish.
        """
        event.id = str(len(self._history))
        self._history.append(event)
        logger.debug("event_published", topic=event.topic, id=event.id)
        await self._dispatch(event)

    async def _dispatch(self, event: RuntimeEvent) -> None:
        """Distributes event payload to matching listeners."""
        tasks = []
        for pattern, callbacks in self._subscribers.items():
            if self._match_topic(pattern, event.topic):
                for callback in callbacks:
                    try:
                        if inspect.iscoroutinefunction(callback):
                            tasks.append(callback(event))
                        else:
                            callback(event)
                    except Exception as error:
                        logger.error(
                            "event_dispatch_failed",
                            topic=event.topic,
                            error=str(error),
                        )

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def _match_topic(self, pattern: str, topic: str) -> bool:
        """Verifies if an event topic matches a subscriber pattern.

        Supports '*' (all topics) and trailing wildcard '.*' namespaces.
        """
        if pattern == "*":
            return True
        if pattern.endswith(".*"):
            prefix = pattern[:-2]
            return topic.startswith(prefix)
        return pattern == topic

    def get_history(self) -> List[RuntimeEvent]:
        """Returns the copy list of dispatched event histories."""
        return list(self._history)

    async def replay_events(self, start_index: int) -> None:
        """Re-dispatches historical events starting from a specific list index.

        Args:
            start_index: 0-indexed position in history.
        """
        if start_index < 0 or start_index >= len(self._history):
            return

        replaying_list = self._history[start_index:]
        logger.info(
            "initiating_events_replay",
            start_index=start_index,
            count=len(replaying_list),
        )

        for event in replaying_list:
            await self._dispatch(event)
