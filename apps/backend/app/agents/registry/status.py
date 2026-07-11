"""Enumerate execution statuses of AI agents.
"""

from enum import Enum


class AgentStatus(str, Enum):
    """Enumerate execution statuses of AI agents."""

    REGISTERED = "registered"
    INITIALIZED = "initialized"
    RUNNING = "running"
    BUSY = "busy"
    STOPPED = "stopped"
    FAILED = "failed"
    DISABLED = "disabled"
