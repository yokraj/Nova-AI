"""BaseAgentSDK class containing inherited agent capabilities.
"""

from datetime import datetime, UTC
import logging
import time
from typing import Any, Optional

from app.agent_sdk.configuration import SDKConfiguration
from app.agent_sdk.context import SDKContext
from app.agent_sdk.exceptions import SDKInitializationError
from app.agent_sdk.health import HealthStatus
from app.agent_sdk.lifecycle import LifecycleManager
from app.agent_sdk.metadata import SDKMetadata


class BaseAgentSDK:
    """The enterprise Agent SDK base class inherited by all future AI Agents."""

    def __init__(self, metadata: SDKMetadata, configuration: Optional[SDKConfiguration] = None) -> None:
        """Initializes BaseAgentSDK.

        Args:
            metadata: Identity metadata model.
            configuration: Initial configuration schema model.
        """
        self.metadata = metadata
        self._config = configuration or SDKConfiguration()
        self._context: Optional[SDKContext] = None
        self._logger = logging.getLogger(f"agent_sdk.{metadata.agent_name}")

        self._start_time: Optional[float] = None
        self._last_execution: Optional[datetime] = None
        self._error_count = 0

        self.lifecycle_manager = LifecycleManager(
            startup_callback=self._on_startup,
            shutdown_callback=self._on_shutdown,
        )

    async def initialize(self) -> None:
        """Starts agent lifecycle setup processes.

        Raises:
            SDKInitializationError: If startup transitions fail.
        """
        try:
            await self.lifecycle_manager.startup()
        except Exception as e:
            raise SDKInitializationError(f"Failed to initialize Agent SDK: {str(e)}") from e

    async def shutdown(self) -> None:
        """Shuts down SDK cleaning resources."""
        await self.lifecycle_manager.shutdown()

    def health(self) -> HealthStatus:
        """Returns runtime health status.

        Returns:
            HealthStatus model with uptime and error counts.
        """
        uptime = 0.0
        if self._start_time is not None:
            uptime = time.perf_counter() - self._start_time

        return HealthStatus(
            healthy=self.lifecycle_manager.is_running,
            uptime=uptime,
            last_execution=self._last_execution,
            error_count=self._error_count,
        )

    @property
    def configuration(self) -> SDKConfiguration:
        """Returns the loaded SDKConfiguration."""
        return self._config

    @property
    def context(self) -> Optional[SDKContext]:
        """Returns the current execution context."""
        return self._context

    def set_context(self, context: SDKContext) -> None:
        """Sets the active request context for execution tracing.

        Args:
            context: SDKContext object to map.
        """
        self._context = context
        self._last_execution = datetime.now(UTC)

    def logger(self) -> logging.Logger:
        """Returns the configured SDK logger instance."""
        return self._logger

    async def _on_startup(self) -> None:
        """Internal callback executed on startup."""
        self._start_time = time.perf_counter()

    async def _on_shutdown(self) -> None:
        """Internal callback executed on shutdown."""
        self._start_time = None
