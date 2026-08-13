"""Custom exception hierarchy for AI Operating System Core & Always-On Voice Runtime.
"""


class OSRuntimeError(Exception):
    """Base exception for all Nova AI OS runtime failures."""

    def __init__(self, message: str, error_code: str = "OS_RUNTIME_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class VoiceAuthFailedError(OSRuntimeError):
    """Raised when speaker voice print verification fails."""

    def __init__(self, user_id: str) -> None:
        super().__init__(f"Speaker voice print authentication failed for user '{user_id}'.", "VOICE_AUTH_FAILED")


class ConfirmationDeniedError(OSRuntimeError):
    """Raised when user denies or cancels a sensitive action confirmation hold."""

    def __init__(self, action_type: str) -> None:
        super().__init__(f"Confirmation hold denied for sensitive action '{action_type}'.", "CONFIRMATION_DENIED")


class MicrophoneUnavailableError(OSRuntimeError):
    """Raised when audio capture device or microphone is unreadable or muted."""

    def __init__(self) -> None:
        super().__init__("Audio capture device / microphone is unavailable or muted.", "MIC_UNAVAILABLE")


class MissionCheckpointError(OSRuntimeError):
    """Raised when long-running background mission checkpoint save or recovery fails."""

    def __init__(self, mission_id: str) -> None:
        super().__init__(f"Failed to create or restore checkpoint for mission '{mission_id}'.", "CHECKPOINT_ERROR")
