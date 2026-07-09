"""Core Runtime Kernel for Nova AI.

Bootstraps kernel services subsystems, coordinates system lifecycle states,
and maps diagnostic components.
"""

from typing import Optional
import structlog

from app.runtime.context import RuntimeContext
from app.runtime.diagnostics import RuntimeDiagnostics
from app.runtime.event_bus import RuntimeEventBus
from app.runtime.health_manager import HealthManager
from app.runtime.interfaces import IKernelService
from app.runtime.resource_manager import ResourceManager
from app.runtime.service_registry import ServiceRegistry
from app.runtime.types import KernelState, RuntimeEvent

logger = structlog.get_logger(__name__)


class RuntimeKernel:
    """The Universal AI Operating System core kernel engine."""

    def __init__(self, env: str = "production") -> None:
        """Initializes the RuntimeKernel.

        Args:
            env: Environment configuration string name.
        """
        self.state: KernelState = KernelState.OFFLINE
        self.context: RuntimeContext = RuntimeContext(env=env)

        # Core Subsystems
        self.service_registry: ServiceRegistry = ServiceRegistry()
        self.resource_manager: ResourceManager = ResourceManager()
        self.health_manager: HealthManager = HealthManager()
        self.event_bus: RuntimeEventBus = RuntimeEventBus()
        self.diagnostics: RuntimeDiagnostics = RuntimeDiagnostics(
            self.service_registry, self.resource_manager, self.health_manager
        )

        # Register subsystems
        self.service_registry.register(self.resource_manager)
        self.service_registry.register(self.health_manager)
        self.service_registry.register(self.event_bus)
        self.service_registry.register(self.diagnostics)

    async def boot(self) -> None:
        """Starts startup boot sequence for all registered subsystems."""
        self.state = KernelState.BOOTING
        logger.info("kernel_boot_sequence_initiated")

        await self.service_registry.start_all()

        self.state = KernelState.ONLINE
        logger.info("kernel_boot_sequence_completed")

        # Broadcast kernel boot success
        await self.event_bus.publish(
            RuntimeEvent(
                topic="system.boot",
                sender="kernel",
                payload={"status": "online"},
            )
        )

    async def shutdown(self) -> None:
        """Gracefully halts all registered subsystems in reverse."""
        self.state = KernelState.SHUTTING_DOWN
        logger.info("kernel_shutdown_sequence_initiated")

        try:
            # Broadcast shutdown warning event
            await self.event_bus.publish(
                RuntimeEvent(
                    topic="system.shutdown",
                    sender="kernel",
                    payload={"status": "offline"},
                )
            )
        except Exception as error:
            logger.warn(
                "shutdown_broadcast_failed", error=str(error)
            )

        await self.service_registry.stop_all()

        self.state = KernelState.OFFLINE
        logger.info("kernel_shutdown_sequence_completed")
