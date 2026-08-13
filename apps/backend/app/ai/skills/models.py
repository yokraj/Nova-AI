"""Pydantic data models, enums, and schemas for Universal Skills Marketplace & SDK.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import time
import uuid


class SkillStatus(str, Enum):
    """Enumerate skill lifecycle statuses."""

    AVAILABLE = "AVAILABLE"
    INSTALLED = "INSTALLED"
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"
    UPDATING = "UPDATING"
    ERROR = "ERROR"


class SkillCategory(str, Enum):
    """Enumerate skill classification categories."""

    DEVELOPER_TOOLS = "developer_tools"
    OFFICE_PRODUCTIVITY = "office_productivity"
    BROWSER_OS = "browser_os"
    CREATIVE_MEDIA = "creative_media"
    SOCIAL_COLLABORATION = "social_collaboration"
    UTILITIES = "utilities"
    CUSTOM = "custom"


class PermissionType(str, Enum):
    """Enumerate security permission scopes required by skills."""

    FILESYSTEM = "filesystem"
    NETWORK = "network"
    DESKTOP = "desktop"
    BROWSER = "browser"
    CAMERA = "camera"
    MICROPHONE = "microphone"
    CLIPBOARD = "clipboard"
    EMAIL = "email"
    CALENDAR = "calendar"
    PAYMENTS = "payments"
    SYSTEM_SETTINGS = "system_settings"


class VoiceCommandPhrase(BaseModel):
    """Voice phrase mapping for dynamic Kernel intent registration."""

    phrase: str = Field(...)
    aliases: List[str] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)
    description: str = Field("")


class SkillManifest(BaseModel):
    """Skill package manifest defining capabilities, voice phrases, and permissions."""

    skill_id: str = Field(...)
    name: str = Field(...)
    version: str = Field("1.0.0")
    category: SkillCategory = Field(SkillCategory.DEVELOPER_TOOLS)
    author: str = Field("Nova Ecosystem")
    description: str = Field("")
    permissions: List[PermissionType] = Field(default_factory=list)
    voice_commands: List[VoiceCommandPhrase] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    icon_url: Optional[str] = Field(None)


class SkillMetadata(BaseModel):
    """Skill catalog metadata descriptor."""

    manifest: SkillManifest = Field(...)
    status: SkillStatus = Field(SkillStatus.AVAILABLE)
    install_date: Optional[str] = Field(None)
    last_used: float = Field(default_factory=time.time)
    rating: float = Field(4.8)
    downloads_count: int = Field(1250)


class SkillContext(BaseModel):
    """Execution context provided to skills during invocation."""

    user_id: str = Field("user_primary")
    session_id: str = Field(default_factory=lambda: f"sess_{uuid.uuid4().hex[:8]}")
    working_directory: str = Field(".")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    permissions_granted: List[PermissionType] = Field(default_factory=list)


class SkillRequest(BaseModel):
    """Invocation request payload for a skill."""

    request_id: str = Field(default_factory=lambda: f"req_{uuid.uuid4().hex[:8]}")
    skill_id: str = Field(...)
    action: str = Field("execute")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    context: SkillContext = Field(default_factory=SkillContext)


class SkillResponse(BaseModel):
    """Execution response payload returned by a skill."""

    response_id: str = Field(default_factory=lambda: f"res_{uuid.uuid4().hex[:8]}")
    skill_id: str = Field(...)
    success: bool = Field(True)
    data: Any = Field(None)
    message: str = Field("Skill executed successfully.")
    latency_ms: float = Field(45.0)


class SkillTelemetry(BaseModel):
    """Skill usage metrics and failure statistics."""

    execution_count: int = Field(0)
    failure_count: int = Field(0)
    avg_latency_ms: float = Field(0.0)
    last_executed: float = Field(default_factory=time.time)


class SkillHealth(BaseModel):
    """Health monitor status model."""

    is_healthy: bool = Field(True)
    total_skills_count: int = Field(0)
    enabled_skills_count: int = Field(0)
    voice_commands_count: int = Field(0)
    timestamp: float = Field(default_factory=time.time)


class SkillMetrics(BaseModel):
    """Telemetry collector metrics model."""

    executions: int = Field(0)
    failures: int = Field(0)
    installs: int = Field(0)
    updates: int = Field(0)
    avg_latency_ms: float = Field(0.0)
    timestamp: float = Field(default_factory=time.time)
