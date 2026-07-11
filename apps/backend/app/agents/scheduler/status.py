"""Enumerate job status states.
"""

from enum import Enum


class JobStatus(str, Enum):
    """Enumeration of job lifecycle execution statuses."""

    PENDING = "PENDING"
    SCHEDULED = "SCHEDULED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    TIMEOUT = "TIMEOUT"
