"""Capability-based message router delivering messages to target agent specialties.
"""

import structlog
from typing import Any, List
from app.ai.collaboration.models import StructuredMessage
from app.ai.collaboration.interfaces import IMessageRouter
from app.core.dependency_container import resolve
from app.ai.gateway import IAIGateway

logger = structlog.get_logger("message_router")

class MessageRouter(IMessageRouter):
    """Routes messages to specific agents, planner, gateway, or groups matching capabilities."""

    def __init__(self, bus: Any, registry: Any = None) -> None:
        self.bus = bus
        self._registry = registry

    @property
    def registry(self) -> Any:
        if self._registry is None:
            try:
                gateway = resolve(IAIGateway)
                self._registry = gateway.agents.registry
            except Exception:
                pass
        return self._registry

    async def route(self, message: StructuredMessage) -> None:
        """Delivers structured message to direct agent receiver or group matching required capability."""
        if message.receiver == "all":
            await self.bus.broadcast(message)
            return

        # Direct delivery if receiver is known in registry
        if self.registry and self.registry.exists(message.receiver):
            logger.debug("Routing direct message to receiver", receiver=message.receiver)
            await self.bus.publish(message)
            return

        # Group capability matching routing
        req_cap = message.metadata.get("required_capability")
        if req_cap and self.registry:
            targets = []
            for reg in self.registry.list():
                metadata = reg.metadata
                if metadata and metadata.capabilities:
                    if any(cap.name == req_cap for cap in metadata.capabilities):
                        targets.append(metadata.id)

            if targets:
                logger.info("Routing capability matched message to group", capability=req_cap, receivers=targets)
                for agent_id in targets:
                    cloned = message.model_copy()
                    cloned.receiver = agent_id
                    await self.bus.publish(cloned)
                return

        # Fallback to direct bus dispatch
        await self.bus.publish(message)
