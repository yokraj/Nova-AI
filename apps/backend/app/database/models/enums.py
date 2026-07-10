"""Database schemas enumerations for Nova AI tables.

Defines status state scopes for users, conversation threads, and message roles.
"""

from enum import Enum


class UserStatus(str, Enum):
    """Lifecycle statuses for a User account."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class ConversationStatus(str, Enum):
    """Operating statuses for a Chat Conversation thread."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class MessageRole(str, Enum):
    """The role/actor tag of a conversation message."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class AttachmentType(str, Enum):
    """Supported file upload attachment types."""

    FILE = "file"
    IMAGE = "image"
    CODE = "code"
    PDF = "pdf"
