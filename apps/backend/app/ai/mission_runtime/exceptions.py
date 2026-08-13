"""Custom exception hierarchy for Autonomous Mission & Workflow Engine.
"""


class MissionRuntimeError(Exception):
    """Base exception for all Mission Runtime Engine errors."""

    pass


class MissionNotFoundError(MissionRuntimeError):
    """Raised when target mission ID is not found."""

    pass


class CheckpointSaveFailedError(MissionRuntimeError):
    """Raised when persistent state checkpoint fails to write."""

    pass


class RecoveryFailedError(MissionRuntimeError):
    """Raised when automated recovery fails to restore state."""

    pass


class ApprovalPendingError(MissionRuntimeError):
    """Raised when mission is blocked awaiting explicit user approval."""

    pass


class WorkerExecutionError(MissionRuntimeError):
    """Raised when background worker encounters an unrecoverable crash."""

    pass
