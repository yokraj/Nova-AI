"""Custom exceptions for the Autonomous Execution & Mission Control Engine.
"""

class MissionError(Exception):
    """Base exception for all mission orchestration errors."""
    pass

class QueueError(MissionError):
    """Raised when queue operations fail."""
    pass

class DecisionError(MissionError):
    """Raised when decision logic fails to resolve actions."""
    pass
