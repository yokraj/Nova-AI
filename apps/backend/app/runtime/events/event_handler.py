"""EventHandler interface defining callbacks for system event subscribers.
"""

from abc import ABC, abstractmethod
from app.runtime.events.event import SystemEvent


class EventHandler(ABC):
    """Abstract Base Class establishing contracts for system event handlers."""

    @abstractmethod
    async def handle(self, event: SystemEvent) -> None:
        """Processes the system event.

        Args:
            event: SystemEvent payload.

        Raises:
            HandlerError: If event processing fails.
        """
        pass

    @abstractmethod
    def can_handle(self, event: SystemEvent) -> bool:
        """Determines if this handler can process the given event.

        Args:
            event: SystemEvent payload.

        Returns:
            True if the handler can process this event; False otherwise.
        """
        pass
