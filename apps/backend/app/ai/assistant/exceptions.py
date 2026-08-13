"""Typed exception hierarchy for Autonomous Personal Assistant & Life Management Engine."""


class AssistantEngineError(Exception):
    """Base exception for personal assistant engine errors."""
    pass


class ScheduleConflictError(AssistantEngineError):
    """Raised when a time block schedule conflict occurs."""
    pass


class ReminderError(AssistantEngineError):
    """Raised when reminder creation or dispatch fails."""
    pass


class TaskNotFoundError(AssistantEngineError):
    """Raised when a specified task ID cannot be found."""
    pass


class GoalTrackingError(AssistantEngineError):
    """Raised when goal tracking metrics fail to update."""
    pass


class ContextResolutionError(AssistantEngineError):
    """Raised when personal life context resolution fails."""
    pass
