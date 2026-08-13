"""Database schemas enumerations for Nova AI tables.

Defines status state scopes for users, conversation threads, message roles,
and dashboard monitoring telemetry.
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


# Dashboard Telemetry Enums


class EventSeverity(str, Enum):
    """Severity levels for dashboard events and alerts."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class NotificationPriority(str, Enum):
    """Priority levels for dashboard notifications."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class HealthStatus(str, Enum):
    """Health diagnostic statuses for dashboard system components."""

    HEALTHY = "healthy"
    WARNING = "warning"
    DEGRADED = "degraded"
    OFFLINE = "offline"


class ResourceType(str, Enum):
    """Hardware and OS resource types tracked in dashboard telemetry."""

    CPU = "cpu"
    GPU = "gpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    PROCESS = "process"
