"""Exceptions specific to the Agent SDK Prompt Framework.
"""

from app.ai.shared import AIException


class PromptException(AIException):
    """Base exception for all prompt framework operations."""

    pass


class PromptValidationError(PromptException):
    """Raised when prompt validation fails."""

    pass


class PromptLoadingError(PromptException):
    """Raised when loading prompt templates fails."""

    pass


class PromptRenderingError(PromptException):
    """Raised when rendering prompt variables fails."""

    pass
