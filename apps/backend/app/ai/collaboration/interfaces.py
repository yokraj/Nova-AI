"""Abstract interfaces for components of the Collaboration Engine.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine, Dict, List, Optional
from app.ai.collaboration.models import StructuredMessage, NegotiationBid

class ICommunicationBus(ABC):
    """Abstract local communication bus."""

    @abstractmethod
    async def publish(self, message: StructuredMessage) -> None:
        """Publishes a structured message to matching listeners."""
        pass

    @abstractmethod
    def subscribe(self, message_type: str, callback: Callable[[StructuredMessage], Coroutine[Any, Any, None]]) -> None:
        """Subscribes an async callback to target message type."""
        pass

    @abstractmethod
    def unsubscribe(self, message_type: str, callback: Callable[[StructuredMessage], Coroutine[Any, Any, None]]) -> None:
        """Unsubscribes a callback from target message type."""
        pass

class IMessageRouter(ABC):
    """Abstract capability-aware message router."""

    @abstractmethod
    async def route(self, message: StructuredMessage) -> None:
        """Routes message to specific receiver or groups based on rules."""
        pass

class IConversationManager(ABC):
    """Abstract conversation lifecycle tracker."""

    @abstractmethod
    def record_message(self, message: StructuredMessage) -> None:
        """Logs message to active thread histories."""
        pass

    @abstractmethod
    def get_thread_history(self, correlation_id: str) -> List[StructuredMessage]:
        """Returns message logs history for target thread."""
        pass

class INegotiationEngine(ABC):
    """Abstract task ownership negotiator."""

    @abstractmethod
    async def negotiate_ownership(self, task_id: str, capabilities: List[str]) -> str:
        """Negotiates workload ownership and returns resolved assignee agent ID."""
        pass

class IConsensusEngine(ABC):
    """Abstract consensus processor."""

    @abstractmethod
    async def seek_consensus(self, correlation_id: str, proposal: str, mode: str) -> bool:
        """Coordinates voting and returns boolean consensus resolution."""
        pass
