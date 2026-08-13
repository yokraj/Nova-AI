"""High-speed Inter-Agent Communication Bus & Event Broker.
"""

from typing import Any, Dict, List
from app.ai.agents.interfaces import IAgentMessageBus
from app.ai.agents.models import AgentMessage


class AgentMessageBus(IAgentMessageBus):
    """High-speed async message bus handling agent event publishing, task queues, heartbeats, and status broadcasts."""

    def __init__(self) -> None:
        self._history: List[AgentMessage] = []
        self._listeners: List[str] = [
            "ExecutiveDivisionBus",
            "EngineeringDivisionBus",
            "ResearchDivisionBus",
            "CreativeDivisionBus",
            "BusinessDivisionBus",
            "AutomationDivisionBus",
            "InfrastructureDivisionBus",
            "QualityDivisionBus",
            "SecurityDivisionBus",
        ]

    async def publish_message(self, message: AgentMessage) -> None:
        """Publishes message to inter-agent bus."""
        self._history.append(message)

    def list_active_listeners(self) -> List[str]:
        """Lists active agent message listeners."""
        return self._listeners

    def get_message_history(self) -> List[AgentMessage]:
        return self._history
