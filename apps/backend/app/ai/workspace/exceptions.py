"""Custom exception hierarchy for Enterprise Workspace & Remote AI Orchestration Platform.
"""


class WorkspaceError(Exception):
    """Base exception for all Workspace Engine errors."""

    pass


class PermissionDeniedError(WorkspaceError):
    """Raised when an operation violates member role permissions."""

    pass


class RemoteExecutionError(WorkspaceError):
    """Raised when remote node execution fails or times out."""

    pass


class SyncConflictError(WorkspaceError):
    """Raised when concurrent editing conflict cannot be automatically resolved."""

    pass


class WorkspaceNotFoundError(WorkspaceError):
    """Raised when target workspace ID does not exist."""

    pass
