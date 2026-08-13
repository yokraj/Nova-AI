"""Custom domain exceptions for the Debugging & Root Cause Analysis Engine.
"""


class DebuggingError(Exception):
    """Base exception for all debugging failures."""
    pass


class RootCauseError(DebuggingError):
    """Raised when root cause parsing or traceback analysis fails."""
    pass


class StackTraceError(DebuggingError):
    """Raised when stack trace extraction or string parsing fails."""
    pass


class RepairGenerationError(DebuggingError):
    """Raised when repair suggestion generation fails."""
    pass


class RepairValidationError(DebuggingError):
    """Raised when validating a generated patch fails compilation or style validation."""
    pass


class DependencyAnalysisError(DebuggingError):
    """Raised when dependency check or manifest validations fail."""
    pass


class ImportValidationError(DebuggingError):
    """Raised when validating modules imports rules fails."""
    pass


class RuntimeAnalysisError(DebuggingError):
    """Raised when runtime tracebacks or scheduling issues analysis fails."""
    pass


class MemoryAnalysisError(DebuggingError):
    """Raised when memory leak detection or large allocations tracing fails."""
    pass


class PerformanceAnalysisError(DebuggingError):
    """Raised when performance profiling or recursion depth check fails."""
    pass


class KnowledgeBaseError(DebuggingError):
    """Raised when loading or writing to local resolutions database fails."""
    pass
