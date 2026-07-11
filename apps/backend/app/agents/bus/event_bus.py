"""AgentEventBus managing asynchronous event publish-subscribe.
"""

import asyncio
import inspect
from typing import Optional

from app.agents.bus.message import AgentEvent
from app.agents.bus.subscription import SubscriptionManager, EventListener
from app.agents.bus.exceptions import MessageValidationError


class AgentEventBus:
    """Central event bus for publishing, subscribing, and dispatching events between agents."""

    def __init__(self, subscription_manager: Optional[SubscriptionManager] = None) -> None:
        """Initializes AgentEventBus.

        Args:
            subscription_manager: Optional SubscriptionManager. If None, creates a default one.
        """
        self.subscription_manager = subscription_manager or SubscriptionManager()

    def subscribe(self, topic: str, listener: EventListener) -> None:
        """Subscribes an event listener to a topic.

        Args:
            topic: Target event topic name.
            listener: Callable handling AgentEvent.
        """
        self.subscription_manager.register(topic, listener)

    def unsubscribe(self, topic: str, listener: EventListener) -> None:
        """Unsubscribes an event listener from a topic.

        Args:
            topic: Target event topic name.
            listener: Callback to remove.
        """
        self.subscription_manager.unregister(topic, listener)

    async def publish(self, event: AgentEvent) -> None:
        """Publishes an event to the bus, triggering registered listeners.

        Args:
            event: AgentEvent metadata payload.

        Raises:
            MessageValidationError: If event lacks topic or source.
        """
        if not event.topic or not event.source:
            raise MessageValidationError("Event must have a valid topic and source.")

        await self.dispatch(event)

    async def broadcast(self, event: AgentEvent) -> None:
        """Publishes an event to a global wildcard topic.

        Args:
            event: AgentEvent payload details.
        """
        broadcast_event = event.model_copy(update={"topic": "*"})
        await self.publish(broadcast_event)

    async def dispatch(self, event: AgentEvent) -> None:
        """Dispatches the event to all matching listeners concurrently.

        Args:
            event: AgentEvent to dispatch.
        """
        listeners = self.subscription_manager.listeners(event.topic)
        if not listeners:
            return

        tasks = [self._execute_listener(listener, event) for listener in listeners]
        await asyncio.gather(*tasks)

    async def _execute_listener(self, listener: EventListener, event: AgentEvent) -> None:
        """Safely executes a single listener callback.

        Args:
            listener: Event listener callback.
            event: AgentEvent payload.
        """
        try:
            if inspect.iscoroutinefunction(listener):
                await listener(event)
            else:
                listener(event)
        except Exception:

            # Prevent failures in one listener from crashing the whole dispatch flow.
            pass

