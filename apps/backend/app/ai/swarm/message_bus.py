"""Message Bus handling inter-agent publish/subscribe and point-to-point messaging."""

from typing import Callable, Dict, List
import structlog

from app.ai.swarm.models import SwarmMessage

logger = structlog.get_logger("message_bus")


class MessageBus:
    """In-process pub/sub message bus for inter-agent communication."""

    def __init__(self) -> None:
        self._listeners: Dict[str, List[Callable[[SwarmMessage], None]]] = {}
        self._history: List[SwarmMessage] = []

    def subscribe(self, topic: str, callback: Callable[[SwarmMessage], None]) -> None:
        """Subscribe agent callback to topic."""
        if topic not in self._listeners:
            self._listeners[topic] = []
        self._listeners[topic].append(callback)

    def publish(self, message: SwarmMessage) -> None:
        """Publish message onto bus."""
        self._history.append(message)
        logger.debug("Published swarm message", sender=message.sender_id, topic=message.topic)
        callbacks = self._listeners.get(message.topic, []) + self._listeners.get("broadcast", [])
        for cb in callbacks:
            try:
                cb(message)
            except Exception as e:
                logger.error("Message bus handler error", error=str(e))
