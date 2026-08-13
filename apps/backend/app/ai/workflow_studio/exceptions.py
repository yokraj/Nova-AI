"""Custom exception hierarchy for Universal Workflow Learning & No-Code Automation Studio.
"""


class WorkflowStudioError(Exception):
    """Base exception for all Workflow Studio errors."""

    pass


class RecordingError(WorkflowStudioError):
    """Raised when workflow event recording fails or is interrupted."""

    pass


class ExecutionError(WorkflowStudioError):
    """Raised when workflow playback or action step execution fails."""

    pass


class ValidationError(WorkflowStudioError):
    """Raised when workflow DAG or variable validation fails."""

    pass


class ImportExportError(WorkflowStudioError):
    """Raised when workflow JSON/YAML import or export fails."""

    pass
