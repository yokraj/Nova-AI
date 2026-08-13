"""Communication Manager orchestrating direct and broadcast inter-agent messages."""

import structlog

from app.ai.swarm.message_bus import MessageBus
from app.ai.swarm.models import SwarmMessage

logger = structlog.get_logger("communication_manager")


class CommunicationManager:
    """Orchestrates inter-agent communication channels."""

    def __init__(self) -> None:
        self.bus = MessageBus()

    async def send_direct_message(self, sender_id: str, receiver_id: str, topic: str, payload: dict) -> SwarmMessage:
        """Send direct message between agents."""
        msg = SwarmMessage(sender_id=sender_id, receiver_id=receiver_id, topic=topic, payload=payload)
        self.bus.publish(msg)
        return msg

    async def broadcast_message(self, sender_id: str, topic: str, payload: dict) -> SwarmMessage:
        """Broadcast message to all swarm agents."""
        msg = SwarmMessage(sender_id=sender_id, receiver_id="broadcast", topic=topic, payload=payload)
        self.bus.publish(msg)
        return msg
