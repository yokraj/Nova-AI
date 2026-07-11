"""SubscriptionManager matching listeners to event topics.
"""

from typing import Awaitable, Callable, Dict, List, Set
from app.agents.bus.message import AgentEvent
from app.agents.bus.exceptions import SubscriptionError

# Define listener callback type
EventListener = Callable[[AgentEvent], Awaitable[None]]


class SubscriptionManager:
    """Manages event topic subscriptions and event listeners mapping."""

    def __init__(self) -> None:
        """Initializes SubscriptionManager."""
        self._subscriptions: Dict[str, Set[EventListener]] = {}

    def register(self, topic: str, listener: EventListener) -> None:
        """Registers a listener callback for a specific event topic.

        Args:
            topic: Target event topic name.
            listener: Async callback handling AgentEvent.

        Raises:
            SubscriptionError: If the listener is invalid or already registered.
        """
        if not callable(listener):
            raise SubscriptionError("Listener must be callable.")
        if topic not in self._subscriptions:
            self._subscriptions[topic] = set()
        if listener in self._subscriptions[topic]:
            raise SubscriptionError(f"Listener already registered for topic '{topic}'.")
        self._subscriptions[topic].add(listener)

    def unregister(self, topic: str, listener: EventListener) -> None:
        """Unregisters a listener callback from a topic.

        Args:
            topic: Target event topic name.
            listener: Registered callback.

        Raises:
            SubscriptionError: If the listener is not registered for the topic.
        """
        if topic not in self._subscriptions or listener not in self._subscriptions[topic]:
            raise SubscriptionError(f"Listener not found for topic '{topic}'.")
        self._subscriptions[topic].remove(listener)
        if not self._subscriptions[topic]:
            del self._subscriptions[topic]

    def listeners(self, topic: str) -> List[EventListener]:
        """Returns list of listeners registered for a specific topic or matching glob/prefix topics.

        Args:
            topic: Target event topic name.

        Returns:
            List of registered callbacks.
        """
        matched: List[EventListener] = []
        # Exact match
        if topic in self._subscriptions:
            matched.extend(self._subscriptions[topic])

        # Glob match (e.g., matching 'agent.*' for topic 'agent.chat')
        for sub_topic, callbacks in self._subscriptions.items():
            if sub_topic != topic and sub_topic.endswith("*"):
                prefix = sub_topic[:-1]
                if topic.startswith(prefix):
                    matched.extend(callbacks)

        return list(set(matched))
