"""Typed exception hierarchy for Ambient Intelligence & Continuous Voice Assistant."""


class AmbientEngineError(Exception):
    """Base exception for ambient engine errors."""
    pass


class MicrophoneError(AmbientEngineError):
    """Raised when continuous microphone listener fails."""
    pass


class WakeWordDetectionError(AmbientEngineError):
    """Raised when wake word runtime encounters an error."""
    pass


class PrivacyModeError(AmbientEngineError):
    """Raised when an operation is blocked by active Privacy Mode."""
    pass


class ConversationSessionError(AmbientEngineError):
    """Raised when a multi-turn voice session fails."""
    pass
