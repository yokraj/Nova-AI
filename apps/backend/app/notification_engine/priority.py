"""Notification Priority Manager Module.

Calculates, escalates, downgrades, and maps notification severity priority levels
(LOW, NORMAL, HIGH, URGENT) based on event payload threshold rules.
"""

from enum import Enum
from typing import Any, Dict, Optional
import structlog

logger = structlog.get_logger(__name__)


class NotificationPriorityLevel(str, Enum):
    """Notification priority severity levels."""

    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"

    @property
    def rank(self) -> int:
        """Numeric rank ordering (higher integer = higher priority)."""
        ranks = {"LOW": 1, "NORMAL": 2, "HIGH": 3, "URGENT": 4}
        return ranks[self.value]


class NotificationPriorityManager:
    """Manages priority classification, escalation, and severity rules."""

    def __init__(self, thresholds: Optional[Dict[str, float]] = None) -> None:
        self.thresholds = thresholds or {
            "cpu_high": 85.0,
            "cpu_urgent": 95.0,
            "memory_high": 85.0,
            "memory_urgent": 95.0,
            "disk_high": 85.0,
            "disk_urgent": 95.0,
        }
        logger.info("priority_manager_initialized", thresholds=self.thresholds)

    def calculate_priority(self, event_type: str, payload: Dict[str, Any]) -> NotificationPriorityLevel:
        """Calculates severity level based on event type and payload metrics."""
        ev = event_type.lower()

        # 1. Critical System / Security Events -> URGENT
        if any(keyword in ev for keyword in ["security", "failure", "crash", "urgent", "offline", "overheating"]):
            return NotificationPriorityLevel.URGENT

        # 2. Hardware Resource Threshold Checks
        if "cpu" in payload and isinstance(payload["cpu"], (int, float)):
            cpu = float(payload["cpu"])
            if cpu >= self.thresholds.get("cpu_urgent", 95.0):
                return NotificationPriorityLevel.URGENT
            if cpu >= self.thresholds.get("cpu_high", 85.0):
                return NotificationPriorityLevel.HIGH

        if "memory" in payload and isinstance(payload["memory"], (int, float)):
            mem = float(payload["memory"])
            if mem >= self.thresholds.get("memory_urgent", 95.0):
                return NotificationPriorityLevel.URGENT
            if mem >= self.thresholds.get("memory_high", 85.0):
                return NotificationPriorityLevel.HIGH

        if "disk" in payload and isinstance(payload["disk"], (int, float)):
            disk = float(payload["disk"])
            if disk >= self.thresholds.get("disk_urgent", 95.0):
                return NotificationPriorityLevel.URGENT
            if disk >= self.thresholds.get("disk_high", 85.0):
                return NotificationPriorityLevel.HIGH

        # 3. High Severity Event Types -> HIGH
        if any(keyword in ev for keyword in ["degradation", "error", "warning", "high"]):
            return NotificationPriorityLevel.HIGH

        # 4. Low Severity Event Types -> LOW
        if any(keyword in ev for keyword in ["info", "startup", "completed", "success"]):
            return NotificationPriorityLevel.LOW

        return NotificationPriorityLevel.NORMAL

    def escalate(self, current_priority: NotificationPriorityLevel) -> NotificationPriorityLevel:
        """Escalates priority level up by one severity rank."""
        order = [
            NotificationPriorityLevel.LOW,
            NotificationPriorityLevel.NORMAL,
            NotificationPriorityLevel.HIGH,
            NotificationPriorityLevel.URGENT,
        ]
        idx = order.index(current_priority)
        if idx < len(order) - 1:
            return order[idx + 1]
        return NotificationPriorityLevel.URGENT

    def downgrade(self, current_priority: NotificationPriorityLevel) -> NotificationPriorityLevel:
        """Downgrades priority level down by one severity rank."""
        order = [
            NotificationPriorityLevel.LOW,
            NotificationPriorityLevel.NORMAL,
            NotificationPriorityLevel.HIGH,
            NotificationPriorityLevel.URGENT,
        ]
        idx = order.index(current_priority)
        if idx > 0:
            return order[idx - 1]
        return NotificationPriorityLevel.LOW

    def apply_rules(self, priority: NotificationPriorityLevel, context: Dict[str, Any]) -> NotificationPriorityLevel:
        """Applies contextual override rules (e.g. repeated failure escalates)."""
        fail_count = context.get("consecutive_failures", 0)
        if fail_count >= 3:
            return self.escalate(priority)
        return priority
