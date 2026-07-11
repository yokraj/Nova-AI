"""SoftwareEngineerState enum tracking agent activity status.
"""

from enum import Enum


class SoftwareEngineerState(str, Enum):
    """Standard tracking states for the Software Engineering Agent."""

    IDLE = "Idle"
    THINKING = "Thinking"
    PLANNING = "Planning"
    EXECUTING = "Executing"
    WAITING = "Waiting"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"
