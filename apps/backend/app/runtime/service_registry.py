"""Subsystem Registry for registered Kernel Services.

Handles service registrations, dependency lookups, and lifecycle execution triggers.
"""

from typing import Dict, List, Optional
import structlog

from app.runtime.exceptions import ServiceRegistrationException
from app.runtime.interfaces import IKernelService

logger = structlog.get_logger(__name__)


class ServiceRegistry:
    """Registry maintaining references to all active subsystems."""

    def __init__(self) -> None:
        self._services: Dict[str, IKernelService] = {}

    def register(self, service: IKernelService) -> None:
        """Registers a kernel service subsystem.

        Args:
            service: An instance implementing IKernelService.

        Raises:
            ServiceRegistrationException: If registration fails due to collision.
        """
        name = service.name
        if name in self._services:
            logger.error(
                "service_registration_failed",
                service=name,
                reason="Duplicate service registration",
            )
            raise ServiceRegistrationException(
                f"Kernel Service '{name}' is already registered."
            )
        self._services[name] = service
        logger.info("service_registered", service=name)

    def get(self, name: str) -> Optional[IKernelService]:
        """Retrieves a registered service instance by name.

        Args:
            name: The unique service name identifier.

        Returns:
            The requested service subclass instance, or None.
        """
        return self._services.get(name)

    def list_services(self) -> List[str]:
        """Lists the names of all registered services."""
        return list(self._services.keys())

    async def start_all(self) -> None:
        """Invokes startup sequences on all registered services."""
        for name, service in self._services.items():
            logger.info("starting_kernel_service", service=name)
            await service.start()

    async def stop_all(self) -> None:
        """Invokes shutdown sequences on all registered services in reverse."""
        for name, service in reversed(list(self._services.items())):
            logger.info("stopping_kernel_service", service=name)
            await service.stop()
