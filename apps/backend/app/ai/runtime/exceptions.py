"""Custom exception hierarchy for Real AI Runtime Integration & Execution Platform.
"""


class RuntimeEngineError(Exception):
    """Base exception for all AI Runtime Engine errors."""

    pass


class ModelNotLoadedError(RuntimeEngineError):
    """Raised when an inference request is routed to an unloaded model."""

    pass


class ResourceAllocationError(RuntimeEngineError):
    """Raised when GPU VRAM or System RAM allocation fails."""

    pass


class DownloadFailedError(RuntimeEngineError):
    """Raised when model checkpoint download or verification fails."""

    pass


class InferenceError(RuntimeEngineError):
    """Raised when model inference fails during execution."""

    pass
