"""Custom domain exceptions for the Conversation bounded context.
"""

from app.runtime.exceptions import KernelException


class ConversationException(KernelException):
    """Base exception for all conversation bounded context errors."""

    pass


class ConversationNotFoundError(ConversationException):
    """Raised when a conversation thread is not found or soft-deleted."""

    pass


class ConversationAccessDeniedError(ConversationException):
    """Raised when a user attempts to access a conversation they do not own."""

    pass


class ConversationArchivedError(ConversationException):
    """Raised when trying to post messages or edit archived conversations."""

    pass


class ConversationValidationError(ConversationException):
    """Raised when request validation rules or constraints are violated."""

    pass
