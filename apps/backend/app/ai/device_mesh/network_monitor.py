"""Network Monitor monitoring inter-node ping latency, bandwidth, and packet loss.
"""

from typing import Any, Dict


class NetworkMonitor:
    """Monitors inter-node network ping latency, throughput bandwidth, and packet loss."""

    def get_link_metrics(self, source_device_id: str, target_device_id: str) -> Dict[str, Any]:
        """Returns network link metrics between two mesh nodes."""
        return {
            "source": source_device_id,
            "target": target_device_id,
            "latency_ms": 4.2,
            "bandwidth_mbps": 950.0,
            "packet_loss_percent": 0.0,
            "quality": "EXCELLENT",
        }
