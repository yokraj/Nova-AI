"""Telemetry metrics collector for Universal Device Mesh Platform.
"""

import time
from app.ai.device_mesh.models import DeviceMeshMetrics


class DeviceMeshMetricsTracker:
    """Collects total devices, paired devices, routed tasks, and failover events."""

    def __init__(self) -> None:
        self._total_devices = 0
        self._paired_devices = 0
        self._routed_tasks = 0
        self._failover_events = 0

    def record_device_registered(self) -> None:
        """Records device registration."""
        self._total_devices += 1

    def record_device_paired(self) -> None:
        """Records device paired."""
        self._paired_devices += 1

    def record_task_routed(self) -> None:
        """Records task routed."""
        self._routed_tasks += 1

    def record_failover_event(self) -> None:
        """Records failover event."""
        self._failover_events += 1

    def get_metrics(self) -> DeviceMeshMetrics:
        """Returns current DeviceMeshMetrics snapshot."""
        return DeviceMeshMetrics(
            total_devices=self._total_devices,
            paired_devices=self._paired_devices,
            routed_tasks=self._routed_tasks,
            failover_events=self._failover_events,
            timestamp=time.time(),
        )
