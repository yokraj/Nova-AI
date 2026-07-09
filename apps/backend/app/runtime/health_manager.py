"""Health Manager subsystem for Nova AI Runtime Kernel.

Tracks diagnostic heartbeats and checks system services availability.
"""

import time
from typing import Dict
import structlog

from app.runtime.interfaces import IKernelService

logger = structlog.get_logger(__name__)


class HealthManager(IKernelService):
    """Monitors running service heartbeats and records system status reports."""

    def __init__(self) -> None:
        self._heartbeats: Dict[str, float] = {}
        self._failures: Dict[str, int] = {}

    async def start(self) -> None:
        """Starts the health manager diagnostics loop."""
        logger.info("health_manager_started")

    async def stop(self) -> None:
        """Flushes tracked heartbeat registries."""
        self._heartbeats.clear()
        self._failures.clear()
        logger.info("health_manager_stopped")

    @property
    def name(self) -> str:
        """Unique service name identifier."""
        return "health_manager"

    def record_heartbeat(self, service_name: str) -> None:
        """Records a successful heartbeat sample.

        Args:
            service_name: Name of reporting kernel service.
        """
        self._heartbeats[service_name] = time.time()
        self._failures[service_name] = 0
        logger.debug("service_heartbeat_recorded", service=service_name)

    def record_failure(self, service_name: str) -> None:
        """Records a service heartbeat failure tick.

        Args:
            service_name: Name of reporting service.
        """
        self._failures[service_name] = self._failures.get(service_name, 0) + 1
        logger.warn(
            "service_heartbeat_failed",
            service=service_name,
            consecutive_failures=self._failures[service_name],
        )

    def is_healthy(self, service_name: str) -> bool:
        """Determines if a service is in a healthy operating state.

        Args:
            service_name: Target service identifier name.

        Returns:
            True if healthy; False if consecutive failures limit (3) exceeded.
        """
        # A service is deemed unhealthy if it registers more than 3 consecutive failures
        return self._failures.get(service_name, 0) < 3

    def get_service_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Returns consolidated health metrics mapping for all tracked services."""
        statuses = {}
        for service_name in set(self._heartbeats.keys()).union(
            self._failures.keys()
        ):
            last_hb = self._heartbeats.get(service_name, 0.0)
            failures = self._failures.get(service_name, 0)
            statuses[service_name] = {
                "last_heartbeat": last_hb,
                "consecutive_failures": failures,
                "is_healthy": failures < 3,
            }
        return statuses


from typing import Any
