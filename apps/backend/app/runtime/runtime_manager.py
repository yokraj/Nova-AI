"""Runtime Manager subsystem for dynamic Capabilities lifecycles in Nova AI.

Coordinates capabilities registrations, initializes them with Contexts,
and verifies transition states.
"""

from typing import Dict, List, Optional
import structlog

from app.runtime.exceptions import CapabilityException
from app.runtime.interfaces import ICapability
from app.runtime.kernel import RuntimeKernel
from app.runtime.types import RuntimeEvent

logger = structlog.get_logger(__name__)


class RuntimeManager:
    """Manages register allocations and operations on dynamic SDK capabilities."""

    def __init__(self, kernel: RuntimeKernel) -> None:
        """Initializes the RuntimeManager.

        Args:
            kernel: The active RuntimeKernel instance.
        """
        self.kernel = kernel
        self._capabilities: Dict[str, ICapability] = {}

    async def register_capability(self, capability: ICapability) -> None:
        """Registers a dynamic SDK capability.

        Args:
            capability: Implementing class instance of ICapability.

        Raises:
            CapabilityException: If capability ID has already been registered.
        """
        cap_id = capability.get_id()
        if cap_id in self._capabilities:
            logger.error(
                "capability_registration_failed",
                capability_id=cap_id,
                reason="Duplicate capability ID",
            )
            raise CapabilityException(
                f"SDK Capability with ID '{cap_id}' is already registered."
            )

        self._capabilities[cap_id] = capability

        # Initialize the capability using the kernel context parameters
        await capability.initialize(self.kernel.context)

        logger.info("capability_registered", capability_id=cap_id)

        # Dispatch registration event
        await self.kernel.event_bus.publish(
            RuntimeEvent(
                topic="capability.registered",
                sender="runtime_manager",
                payload={"capability_id": cap_id},
            )
        )

    def get_capability(self, cap_id: str) -> Optional[ICapability]:
        """Retrieves a capability by ID.

        Args:
            cap_id: Unique capability identifier.

        Returns:
            The ICapability instance, or None.
        """
        return self._capabilities.get(cap_id)

    def list_capabilities(self) -> List[str]:
        """Lists IDs of all loaded capabilities."""
        return list(self._capabilities.keys())

    async def activate_capability(self, cap_id: str) -> None:
        """Activates a registered capability.

        Args:
            cap_id: Unique capability identifier.
        """
        capability = self.get_capability(cap_id)
        if not capability:
            raise CapabilityException(
                f"Cannot activate: Capability ID '{cap_id}' not found."
            )

        await capability.activate()
        logger.info("capability_activated", capability_id=cap_id)

        await self.kernel.event_bus.publish(
            RuntimeEvent(
                topic="capability.activated",
                sender="runtime_manager",
                payload={"capability_id": cap_id},
            )
        )

    async def suspend_capability(self, cap_id: str) -> None:
        """Suspends a running capability.

        Args:
            cap_id: Unique capability identifier.
        """
        capability = self.get_capability(cap_id)
        if not capability:
            raise CapabilityException(
                f"Cannot suspend: Capability ID '{cap_id}' not found."
            )

        await capability.suspend()
        logger.info("capability_suspended", capability_id=cap_id)

        await self.kernel.event_bus.publish(
            RuntimeEvent(
                topic="capability.suspended",
                sender="runtime_manager",
                payload={"capability_id": cap_id},
            )
        )

    async def terminate_capability(self, cap_id: str) -> None:
        """Halts and terminates a capability.

        Args:
            cap_id: Unique capability identifier.
        """
        capability = self.get_capability(cap_id)
        if not capability:
            raise CapabilityException(
                f"Cannot terminate: Capability ID '{cap_id}' not found."
            )

        await capability.terminate()
        logger.info("capability_terminated", capability_id=cap_id)

        await self.kernel.event_bus.publish(
            RuntimeEvent(
                topic="capability.terminated",
                sender="runtime_manager",
                payload={"capability_id": cap_id},
            )
        )
