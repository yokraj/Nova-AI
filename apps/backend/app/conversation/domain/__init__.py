"""Conversation domain package exports for Nova AI.

Exposes domain models and enums.
"""

from app.conversation.domain.enums import ConversationStatus, MessageRole, AttachmentType
from app.conversation.domain.conversation import Conversation
from app.conversation.domain.message import Message
from app.conversation.domain.attachment import Attachment
from app.conversation.domain.exceptions import (
    ConversationException,
    ConversationNotFoundError,
    ConversationAccessDeniedError,
    ConversationArchivedError,
    ConversationValidationError,
)

__all__ = [
    "ConversationStatus",
    "MessageRole",
    "AttachmentType",
    "Conversation",
    "Message",
    "Attachment",
    "ConversationException",
    "ConversationNotFoundError",
    "ConversationAccessDeniedError",
    "ConversationArchivedError",
    "ConversationValidationError",
]
