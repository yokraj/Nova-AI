"""Database Models package exports for Nova AI.

Exposes auditing base schemas, enums, users, conversations, messages, sessions,
rotatable refresh tokens, profiles preferences, AI credentials configurations,
skills, missions, checkpoints, agents, and dashboard monitoring entities.
"""

from app.database.models.enums import (
    UserStatus,
    ConversationStatus,
    MessageRole,
    AttachmentType,
    EventSeverity,
    NotificationPriority,
    HealthStatus,
    ResourceType,
)
from app.database.models.base import BaseEntity
from app.database.models.user import User
from app.database.models.conversation import Conversation
from app.database.models.message import Message
from app.database.models.attachment import Attachment
from app.database.models.session import Session
from app.database.models.refresh_token import RefreshToken
from app.database.models.user_preference import UserPreference
from app.database.models.ai_provider_configuration import AIProviderConfiguration
from app.database.models.memory_model import MemoryModel
from app.database.models.dashboard import (
    DashboardSnapshot,
    SystemMetric,
    ResourceMetric,
    GPUMetric,
    ProcessMetric,
    DashboardEvent,
    DashboardNotification,
    AnalyticsRecord,
    HealthRecord,
    DashboardConfiguration,
)

from app.database.models.skill_model import SkillModel, SkillVersionModel
from app.database.models.mission_model import MissionModel, MissionTaskModel
from app.database.models.mission_checkpoint_model import (
    MissionCheckpointModel,
    MissionApprovalModel,
    MissionRecoveryEventModel,
)
from app.database.models.agent_model import AgentModel, AgentExecutionModel
from app.database.models.audit_model import AuditEventModel

__all__ = [
    "UserStatus",
    "ConversationStatus",
    "MessageRole",
    "AttachmentType",
    "EventSeverity",
    "NotificationPriority",
    "HealthStatus",
    "ResourceType",
    "BaseEntity",
    "User",
    "Conversation",
    "Message",
    "Attachment",
    "Session",
    "RefreshToken",
    "UserPreference",
    "AIProviderConfiguration",
    "MemoryModel",
    "SkillModel",
    "SkillVersionModel",
    "MissionModel",
    "MissionTaskModel",
    "MissionCheckpointModel",
    "MissionApprovalModel",
    "MissionRecoveryEventModel",
    "AgentModel",
    "AgentExecutionModel",
    "AuditEventModel",
    "DashboardSnapshot",
    "SystemMetric",
    "ResourceMetric",
    "GPUMetric",
    "ProcessMetric",
    "DashboardEvent",
    "DashboardNotification",
    "AnalyticsRecord",
    "HealthRecord",
    "DashboardConfiguration",
]
