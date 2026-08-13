"""Anomaly Detector Module.

Detects statistical metric anomalies, z-score spikes, and variance outliers
across hardware resources, health scores, and notification volumes without ML dependencies.
"""

import math
from typing import Any, Dict, List
import structlog

logger = structlog.get_logger(__name__)


class AnomalyDetector:
    """Statistical anomaly detector based on Z-score and Standard Deviation baselines."""

    def __init__(self, z_threshold: float = 2.0) -> None:
        self.z_threshold = z_threshold
        logger.info("anomaly_detector_initialized", z_threshold=z_threshold)

    def _calculate_z_scores(self, values: List[float]) -> List[float]:
        """Calculates Z-score for each value in list."""
        if len(values) < 3:
            return [0.0] * len(values)

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = math.sqrt(variance)

        if std_dev == 0:
            return [0.0] * len(values)

        return [(x - mean) / std_dev for x in values]

    def detect_anomalies_generic(self, metric_name: str, values: List[float]) -> List[Dict[str, Any]]:
        """Detects values exceeding statistical z_threshold."""
        if len(values) < 3:
            return []

        z_scores = self._calculate_z_scores(values)
        anomalies = []

        for idx, (val, z) in enumerate(zip(values, z_scores)):
            if abs(z) >= self.z_threshold:
                anomalies.append({
                    "metric_name": metric_name,
                    "index": idx,
                    "value": round(val, 2),
                    "z_score": round(z, 2),
                    "type": "spike" if z > 0 else "drop",
                    "severity": "CRITICAL" if abs(z) >= 3.0 else "WARNING",
                })

        if anomalies:
            logger.info("anomalies_detected", metric=metric_name, count=len(anomalies))
        return anomalies

    def detect_cpu_anomalies(self, cpu_samples: List[float]) -> List[Dict[str, Any]]:
        """Detects CPU utilization spikes."""
        return self.detect_anomalies_generic("cpu_utilization", cpu_samples)

    def detect_memory_anomalies(self, memory_samples: List[float]) -> List[Dict[str, Any]]:
        """Detects Memory utilization spikes."""
        return self.detect_anomalies_generic("memory_utilization", memory_samples)

    def detect_disk_anomalies(self, disk_samples: List[float]) -> List[Dict[str, Any]]:
        """Detects Disk utilization anomalies."""
        return self.detect_anomalies_generic("disk_utilization", disk_samples)

    def detect_network_anomalies(self, network_samples: List[float]) -> List[Dict[str, Any]]:
        """Detects Network throughput spikes."""
        return self.detect_anomalies_generic("network_throughput", network_samples)

    def detect_health_anomalies(self, health_samples: List[float]) -> List[Dict[str, Any]]:
        """Detects Health score drops."""
        return self.detect_anomalies_generic("health_score", health_samples)

    def detect_notification_spikes(self, notification_counts: List[int]) -> List[Dict[str, Any]]:
        """Detects notification creation volume spikes."""
        float_counts = [float(c) for c in notification_counts]
        return self.detect_anomalies_generic("notification_volume", float_counts)
