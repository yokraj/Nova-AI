"""Fault Detector detecting node crashes, process faults, and network partitions.
"""

from typing import Any, Dict


class FaultDetector:
    """Detects node crashes, process timeouts, and network partition faults."""

    def check_node_fault(self, device_id: str, is_responsive: bool) -> Dict[str, Any]:
        """Evaluates node responsiveness and detects faults."""
        return {
            "device_id": device_id,
            "has_fault": not is_responsive,
            "fault_type": "NONE" if is_responsive else "NODE_TIMEOUT_PARTITION",
        }
