"""Custom exception hierarchy for AI Model Integration Platform & Intelligent Router.
"""


class ModelPlatformError(Exception):
    """Base exception for all AI Model Platform errors."""

    pass


class ModelNotFoundError(ModelPlatformError):
    """Raised when target model ID is not registered."""

    pass


class ModelLoadError(ModelPlatformError):
    """Raised when loading model into RAM/VRAM fails."""

    pass


class ModelRoutingFailedError(ModelPlatformError):
    """Raised when Intelligent Router fails to select an appropriate model."""

    pass


class ProviderExecutionError(ModelPlatformError):
    """Raised when model provider backend encounters an execution error."""

    pass


class OutOfVRAMError(ModelPlatformError):
    """Raised when GPU VRAM capacity is exceeded."""

    pass
