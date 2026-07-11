"""Enumerate job priority levels.
"""

from enum import Enum


class Priority(str, Enum):
    """Enumeration of job priorities."""

    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    @property
    def rank(self) -> int:
        """Numeric rank mapping where higher values represent higher priority."""
        ranks = {
            Priority.LOW: 0,
            Priority.NORMAL: 1,
            Priority.HIGH: 2,
            Priority.CRITICAL: 3,
        }
        return ranks[self]
