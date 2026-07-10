"""Conversation domain enumerations for Nova AI.

Maps statuses, message actors, and file types to database definitions.
"""

from app.database.models.enums import ConversationStatus, MessageRole, AttachmentType

__all__ = ["ConversationStatus", "MessageRole", "AttachmentType"]
