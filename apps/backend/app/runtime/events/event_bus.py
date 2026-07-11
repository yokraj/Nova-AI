"""EventBus managing system-wide event notifications.
"""

import asyncio
from datetime import datetime
import inspect
from typing import Dict, List, Optional, Set

from app.runtime.events.event import SystemEvent
from app.runtime.events.event_handler import EventHandler
from app.runtime.events.event_store import EventStore
from app.runtime.events.exceptions import EventPublishError, EventReplayError, HandlerError
from app.runtime.events.subscription import Subscriber
from app.runtime.events.topics import Topic


class EventBus:
    """Central event bus distributing system-wide telemetry events asynchronously."""

    def __init__(self, event_store: Optional[EventStore] = None) -> None:
        """Initializes EventBus.

        Args:
            event_store: Optional EventStore. If None, creates a default one.
        """
        self.event_store = event_store or EventStore()
        self._subscribers: Dict[Topic, Set[Subscriber]] = {}

    def subscribe(self, topic: Topic, subscriber: Subscriber) -> None:
        """Subscribes a handler or async callback to a specific system topic.

        Args:
            topic: Target topic Enum.
            subscriber: EventHandler instance or async callback callable.
        """
        if topic not in self._subscribers:
            self._subscribers[topic] = set()
        self._subscribers[topic].add(subscriber)

    def unsubscribe(self, topic: Topic, subscriber: Subscriber) -> None:
        """Unsubscribes a subscriber from a topic.

        Args:
            topic: Target topic Enum.
            subscriber: Registered subscriber callback.
        """
        if topic in self._subscribers and subscriber in self._subscribers[topic]:
            self._subscribers[topic].remove(subscriber)
            if not self._subscribers[topic]:
                del self._subscribers[topic]

    async def publish(self, event: SystemEvent) -> None:
        """Publishes a SystemEvent to the bus, appending it to store and notifying subscribers.

        Args:
            event: SystemEvent payload.

        Raises:
            EventPublishError: If publishing or dispatch execution fails.
        """
        if not event.topic or not event.source:
            raise EventPublishError("SystemEvent must contain a valid topic and source.")

        # Persist event
        self.event_store.append(event)

        # Notify subscribers
        subscribers = self._subscribers.get(event.topic, set())
        if subscribers:
            tasks = [self._dispatch_to_subscriber(sub, event) for sub in subscribers]
            await asyncio.gather(*tasks)

    async def publish_batch(self, events: List[SystemEvent]) -> None:
        """Publishes a list of system events concurrently.

        Args:
            events: List of SystemEvents to publish.
        """
        tasks = [self.publish(e) for e in events]
        await asyncio.gather(*tasks)

    async def broadcast(self, event: SystemEvent) -> None:
        """Publishes an event to all registered subscribers across all topics.

        Args:
            event: SystemEvent payload to broadcast.
        """
        # Persist event
        self.event_store.append(event)

        # Retrieve all unique subscribers across all topics
        all_subscribers = set()
        for subs in self._subscribers.values():
            all_subscribers.update(subs)

        if all_subscribers:
            tasks = [self._dispatch_to_subscriber(sub, event, bypass_can_handle=True) for sub in all_subscribers]
            await asyncio.gather(*tasks)

    async def replay(self, topic: Optional[Topic] = None, since: Optional[datetime] = None) -> None:
        """Replays matching historical events from the EventStore back onto subscribers.

        Args:
            topic: Optional topic filter.
            since: Optional starting timestamp.

        Raises:
            EventReplayError: If replaying matching events fails.
        """
        try:
            historical_events = self.event_store.replay(topic=topic, since=since)
            for event in historical_events:
                # Resolve subscribers for this specific event's topic
                subscribers = self._subscribers.get(event.topic, set())
                if subscribers:
                    tasks = [self._dispatch_to_subscriber(sub, event) for sub in subscribers]
                    await asyncio.gather(*tasks)
        except Exception as e:
            raise EventReplayError(f"Failed to replay events: {str(e)}") from e

    async def _dispatch_to_subscriber(
        self, subscriber: Subscriber, event: SystemEvent, bypass_can_handle: bool = False
    ) -> None:
        """Safely dispatches the system event to a single subscriber.

        Args:
            subscriber: Target subscriber callback.
            event: SystemEvent details.
            bypass_can_handle: If True, bypasses can_handle checks on EventHandlers.

        Raises:
            HandlerError: If handler execution throws an error.
        """
        try:
            if isinstance(subscriber, EventHandler):
                if bypass_can_handle or subscriber.can_handle(event):
                    await subscriber.handle(event)
            elif callable(subscriber):
                if inspect.iscoroutinefunction(subscriber):
                    await subscriber(event)
                else:
                    subscriber(event)
        except Exception as e:
            raise HandlerError(f"Subscriber failed executing handler: {str(e)}") from e
