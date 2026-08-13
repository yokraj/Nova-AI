"""Custom exception hierarchy for Universal AI Orchestrator.
"""


class OrchestratorError(Exception):
    """Base exception for all Universal AI Orchestrator failures."""

    def __init__(self, message: str, error_code: str = "ORCHESTRATOR_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ModelNotFoundError(OrchestratorError):
    """Raised when requested model weights or specification cannot be resolved."""

    def __init__(self, model_id: str) -> None:
        super().__init__(f"Model '{model_id}' was not found in registry or local installation directory.", "MODEL_NOT_FOUND")


class ProviderUnavailableError(OrchestratorError):
    """Raised when target provider plugin backend is offline or unreachable."""

    def __init__(self, provider_name: str) -> None:
        super().__init__(f"Provider '{provider_name}' backend daemon or service is offline/unreachable.", "PROVIDER_UNAVAILABLE")


class GPUOutOfMemoryError(OrchestratorError):
    """Raised when available VRAM is insufficient to load requested model."""

    def __init__(self, required_mb: int, available_mb: int) -> None:
        super().__init__(f"GPU Out-Of-Memory: Required {required_mb} MB VRAM, but only {available_mb} MB available.", "GPU_OOM")


class DownloadVerificationError(OrchestratorError):
    """Raised when SHA-256 checksum verification fails after downloading model weights."""

    def __init__(self, model_id: str) -> None:
        super().__init__(f"Checksum integrity verification failed for downloaded model '{model_id}'.", "DOWNLOAD_CHECKSUM_FAILED")
