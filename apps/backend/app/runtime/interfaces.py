"""Abstract structural interfaces for Nova AI Runtime Kernel components.

Declares lifecycle contracts that kernel services and dynamic capabilities SDK
extensions must satisfy.
"""

from abc import ABC, abstractmethod

from app.runtime.types import CapabilityState


class IKernelService(ABC):
    """Contract for core kernel subsystem modules (e.g. registries, managers)."""

    @abstractmethod
    async def start(self) -> None:
        """Starts the service execution and sets up resources allocations."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Gracefully halts the service execution and releases locks."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the unique name identifier of the subsystem.

        Returns:
            The string identifier of the service.
        """
        pass


class ICapability(ABC):
    """Contract for custom SDK capabilities registered in the runtime OS."""

    @abstractmethod
    def get_id(self) -> str:
        """Returns the unique capability ID (e.g. 'text_parser', 'vision_detect').

        Returns:
            The string ID of the capability.
        """
        pass

    @abstractmethod
    def get_state(self) -> CapabilityState:
        """Returns the current state of the capability in its lifecycle.

        Returns:
            The CapabilityState indicator.
        """
        pass

    @abstractmethod
    async def initialize(self, context: Any) -> None:
        """Initializes settings and maps internal context configurations.

        Args:
            context: The active RuntimeContext.
        """
        pass

    @abstractmethod
    async def activate(self) -> None:
        """Activates the capability, setting state to ACTIVE."""
        pass

    @abstractmethod
    async def suspend(self) -> None:
        """Suspends active processing, setting state to SUSPENDED."""
        pass

    @abstractmethod
    async def terminate(self) -> None:
        """De-activates and cleans up the capability, setting state to STOPPED."""
        pass


# Type-hint mappings helper
from typing import Any
