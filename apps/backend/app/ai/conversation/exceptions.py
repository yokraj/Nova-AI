"""Custom exception hierarchy for Conversation & Emotional Intelligence Engine.
"""


class ConversationEngineError(Exception):
    """Base exception for all Conversation Engine errors."""

    pass


class SessionNotFoundError(ConversationEngineError):
    """Raised when a requested conversation session ID is not found."""

    pass


class EmotionDetectionError(ConversationEngineError):
    """Raised when emotion detection fails."""

    pass


class InvalidPersonalityError(ConversationEngineError):
    """Raised when an invalid personality profile is requested."""

    pass


class InterruptionError(ConversationEngineError):
    """Raised when an interruption signal handling fails."""

    pass
