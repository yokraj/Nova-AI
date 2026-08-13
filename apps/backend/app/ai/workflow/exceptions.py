"""Custom exceptions for the Workflow Orchestration Engine.
"""

class WorkflowError(Exception):
    """Base exception for all workflow orchestration errors."""
    pass

class ExecutionError(WorkflowError):
    """Raised when step execution fails."""
    pass

class CheckpointError(WorkflowError):
    """Raised when checkpoint serialization or deserialization fails."""
    pass

class RollbackException(WorkflowError):
    """Raised when step rollbacks fail to restore states."""
    pass
