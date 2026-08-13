"""Local Inter-Agent Communication Bus.
"""

import asyncio
import structlog
from typing import Any, Callable, Coroutine, Dict, List
from app.ai.collaboration.models import StructuredMessage
from app.ai.collaboration.interfaces import ICommunicationBus

logger = structlog.get_logger("communication_bus")

class CommunicationBus(ICommunicationBus):
    """Enables structured directed/broadcast communication with DLQ and message logs."""

    def __init__(self, event_bus: Any = None) -> None:
        self.event_bus = event_bus
        self._listeners: Dict[str, List[Callable[[StructuredMessage], Coroutine[Any, Any, None]]]] = {}
        self.message_history: List[StructuredMessage] = []
        self.dlq: List[StructuredMessage] = []
        self.acknowledgements: Dict[str, List[str]] = {}

    def subscribe(self, message_type: str, callback: Callable[[StructuredMessage], Coroutine[Any, Any, None]]) -> None:
        """Registers listener callback for specific message types."""
        if message_type not in self._listeners:
            self._listeners[message_type] = []
        if callback not in self._listeners[message_type]:
            self._listeners[message_type].append(callback)

    def unsubscribe(self, message_type: str, callback: Callable[[StructuredMessage], Coroutine[Any, Any, None]]) -> None:
        """Removes listener callback."""
        if message_type in self._listeners and callback in self._listeners[message_type]:
            self._listeners[message_type].remove(callback)

    async def publish(self, message: StructuredMessage) -> None:
        """Publishes message to matching listener callbacks and logs history."""
        self.message_history.append(message)
        listeners = self._listeners.get(message.message_type.value, [])

        routed = False
        tasks = []
        for cb in listeners:
            tasks.append(asyncio.create_task(cb(message)))
            routed = True

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for res in results:
                if isinstance(res, Exception):
                    logger.error("Callback task failed on communication bus", error=str(res))
                    self.dlq.append(message)

        if not routed:
            logger.debug("No active subscriptions found. Routing to DLQ.", correlation_id=message.correlation_id)
            self.dlq.append(message)

        # Bridge with core Agent EventBus
        if self.event_bus:
            try:
                await self.event_bus.publish("inter_agent_msg", message)
            except Exception as err:
                logger.error("Core event bus dispatch failed", error=str(err))

    async def broadcast(self, message: StructuredMessage) -> None:
        """Broadcasts message to all subscriber agents."""
        message.receiver = "all"
        await self.publish(message)

    def replay_messages(self, correlation_id: str) -> List[StructuredMessage]:
        """Replays all logged messages belonging to target thread correlation ID."""
        return [msg for msg in self.message_history if msg.correlation_id == correlation_id]

    def acknowledge(self, correlation_id: str, agent_id: str) -> None:
        """Records agent acknowledgement for message thread."""
        if correlation_id not in self.acknowledgements:
            self.acknowledgements[correlation_id] = []
        if agent_id not in self.acknowledgements[correlation_id]:
            self.acknowledgements[correlation_id].append(agent_id)
