"""Change Detector Module.

Evaluates metric value deltas between sampling cycles against configurable
percentage thresholds to determine if real-time WebSocket broadcast is required.
"""

from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class ChangeDetector:
    """Evaluates telemetry value changes against configurable delta thresholds."""

    def __init__(self, threshold: float = 0.01) -> None:
        self.threshold = threshold
        logger.info("change_detector_initialized", threshold=threshold)

    def _values_changed(self, current: Any, previous: Any) -> bool:
        """Determines if a scalar, list, or dict value has changed beyond threshold."""
        if previous is None:
            return True

        if type(current) != type(previous):
            return True

        if isinstance(current, (int, float)) and isinstance(previous, (int, float)):
            if previous == 0:
                return abs(current - previous) > self.threshold
            delta_ratio = abs(current - previous) / abs(previous)
            return delta_ratio >= self.threshold

        if isinstance(current, dict):
            if set(current.keys()) != set(previous.keys()):
                return True
            for k, v in current.items():
                if self._values_changed(v, previous.get(k)):
                    return True
            return False

        if isinstance(current, list):
            if len(current) != len(previous):
                return True
            for item_c, item_p in zip(current, previous):
                if self._values_changed(item_c, item_p):
                    return True
            return False

        return current != previous

    def has_changed(self, current: Dict[str, Any], previous: Optional[Dict[str, Any]]) -> bool:
        """Returns True if current telemetry dict differs significantly from previous."""
        if not previous:
            return True
        return self._values_changed(current, previous)

    def compare_metrics(self, current: Dict[str, Any], previous: Optional[Dict[str, Any]]) -> bool:
        """Compares general metrics dictionary."""
        return self.has_changed(current, previous)

    def compare_resources(self, current: Dict[str, Any], previous: Optional[Dict[str, Any]]) -> bool:
        """Compares resource allocation telemetry (CPU, Memory, Disk, Network)."""
        return self.has_changed(current, previous)

    def compare_health(self, current: Dict[str, Any], previous: Optional[Dict[str, Any]]) -> bool:
        """Compares system component health status."""
        if not previous:
            return True
        # Immediate change if status text changes or score shifts beyond threshold
        return current.get("status") != previous.get("status") or self._values_changed(
            current.get("health_score", 1.0), previous.get("health_score", 1.0)
        )

    def compare_dashboard(self, current: Dict[str, Any], previous: Optional[Dict[str, Any]]) -> bool:
        """Compares consolidated dashboard overview DTO."""
        return self.has_changed(current, previous)

    def compare_processes(self, current: List[Dict[str, Any]], previous: Optional[List[Dict[str, Any]]]) -> bool:
        """Compares process list tables."""
        if previous is None:
            return True
        if len(current) != len(previous):
            return True
        for p_curr, p_prev in zip(current, previous):
            if p_curr.get("pid") != p_prev.get("pid") or abs(p_curr.get("cpu_percent", 0.0) - p_prev.get("cpu_percent", 0.0)) > 2.0:
                return True
        return False

    def compare_gpu(self, current: List[Dict[str, Any]], previous: Optional[List[Dict[str, Any]]]) -> bool:
        """Compares GPU device utilization samples."""
        if previous is None:
            return True
        if len(current) != len(previous):
            return True
        for g_curr, g_prev in zip(current, previous):
            if abs(g_curr.get("load_percent", 0.0) - g_prev.get("load_percent", 0.0)) >= (self.threshold * 100.0):
                return True
        return False
