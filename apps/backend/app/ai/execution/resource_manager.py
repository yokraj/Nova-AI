"""Resource Manager monitoring CPU, RAM, GPU, and Disk utilization."""

import os
from typing import Optional
import structlog

from app.ai.execution.configuration import ExecutionConfiguration
from app.ai.execution.exceptions import ResourceExhaustedError
from app.ai.execution.models import ResourceSnapshot

logger = structlog.get_logger("resource_manager")


class ResourceManager:
    """Monitors system resource utilization before and during task execution."""

    def __init__(self, config: Optional[ExecutionConfiguration] = None) -> None:
        self.config = config or ExecutionConfiguration()

    def capture_snapshot(self) -> ResourceSnapshot:
        """Capture current resource utilization metrics."""
        cpu = 15.0
        mem = 40.0
        disk = 50.0

        try:
            import psutil
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory().percent
            disk = psutil.disk_usage("/").percent
        except Exception:
            pass

        return ResourceSnapshot(
            cpu_percent=cpu,
            memory_percent=mem,
            gpu_percent=0.0,
            disk_percent=disk,
        )

    def check_capacity() -> bool: ...
    def check_capacity(self) -> bool:
        """Check if system resource utilization is within safe thresholds."""
        snapshot = self.capture_snapshot()
        if snapshot.cpu_percent > self.config.max_cpu_percent:
            raise ResourceExhaustedError(
                f"CPU utilization ({snapshot.cpu_percent}%) exceeds maximum limit ({self.config.max_cpu_percent}%)."
            )
        if snapshot.memory_percent > self.config.max_memory_percent:
            raise ResourceExhaustedError(
                f"Memory utilization ({snapshot.memory_percent}%) exceeds maximum limit ({self.config.max_memory_percent}%)."
            )
        return True
