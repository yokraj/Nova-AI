"""Typed exception hierarchy for the Autonomous Skill Execution Runtime."""


class ExecutionError(Exception):
    """Base exception for all execution runtime errors."""
    pass


class TaskExecutionError(ExecutionError):
    """Raised when task or mission execution fails."""
    pass


class StepFailedError(ExecutionError):
    """Raised when an individual execution step fails permanently."""
    pass


class ApprovalRequiredError(ExecutionError):
    """Raised when step execution requires human approval before proceeding."""
    pass


class RollbackError(ExecutionError):
    """Raised when transaction rollback fails to execute compensating steps."""
    pass


class CheckpointError(ExecutionError):
    """Raised when checkpoint creation or restoration fails."""
    pass


class ResourceExhaustedError(ExecutionError):
    """Raised when system resource limits (CPU/RAM/Disk) are exceeded."""
    pass
