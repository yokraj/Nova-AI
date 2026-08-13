"""Custom exception hierarchy for Autonomous AI Software Engineering Company.
"""


class SoftwareCompanyError(Exception):
    """Base exception for all software company failures."""

    def __init__(self, message: str, error_code: str = "SOFTWARE_COMPANY_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ArchitectureValidationError(SoftwareCompanyError):
    """Raised when software architecture blueprint validation fails."""

    def __init__(self, reason: str) -> None:
        super().__init__(f"Architecture blueprint validation failed: {reason}", "ARCH_VALIDATION_FAILED")


class BuildPipelineFailedError(SoftwareCompanyError):
    """Raised when the project factory build pipeline encounters a fatal error."""

    def __init__(self, stage: str, details: str) -> None:
        super().__init__(f"Build pipeline failed at stage '{stage}': {details}", "BUILD_PIPELINE_FAILED")


class AutoFixMaxRetriesExceededError(SoftwareCompanyError):
    """Raised when automated bug fixing exceeds maximum configured retries."""

    def __init__(self, attempts: int) -> None:
        super().__init__(f"Auto-fix debugging exceeded maximum limit of {attempts} attempts.", "AUTOFIX_RETRIES_EXCEEDED")
