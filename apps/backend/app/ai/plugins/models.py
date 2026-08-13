"""Domain models and data schemas for the Universal Plugin Platform."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class PluginStatus(str, Enum):
    """Lifecycle state of a registered plugin."""

    INSTALLED = "installed"
    LOADED = "loaded"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"
    UNINSTALLED = "uninstalled"


class PermissionType(str, Enum):
    """Permission category declared by a plugin."""

    BROWSER = "browser"
    DESKTOP = "desktop"
    FILE_SYSTEM = "file_system"
    CAMERA = "camera"
    MICROPHONE = "microphone"
    NETWORK = "network"
    EMAIL = "email"
    CALENDAR = "calendar"
    CLIPBOARD = "clipboard"
    NOTIFICATIONS = "notifications"
    TERMINAL = "terminal"


class CapabilityType(str, Enum):
    """Type of capability exposed by a plugin."""

    TOOL = "tool"
    SKILL = "skill"
    ACTION = "action"
    COMMAND = "command"


class RiskLevel(str, Enum):
    """Risk severity level associated with a permission or capability."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class PluginPermission(BaseModel):
    """A permission declared by a plugin requirement."""

    permission_type: PermissionType
    description: str
    risk_level: RiskLevel = RiskLevel.LOW
    requires_human_approval: bool = False


class PluginCapability(BaseModel):
    """A capability (tool/skill/action) offered by a plugin."""

    name: str
    description: str
    capability_type: CapabilityType = CapabilityType.TOOL
    parameters_schema: Dict[str, Any] = Field(default_factory=dict)
    required_permissions: List[PermissionType] = Field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.LOW
    voice_intents: List[str] = Field(default_factory=list)


class PluginMetadata(BaseModel):
    """Metadata describing a plugin package."""

    name: str
    version: str = "1.0.0"
    author: str = "Nova AI"
    description: str = ""
    license: str = "MIT"
    homepage: Optional[str] = None
    min_nova_version: str = "3.0.0"
    dependencies: List[str] = Field(default_factory=list)


class PluginSpec(BaseModel):
    """Complete specification of an installed or loaded plugin."""

    plugin_id: str
    metadata: PluginMetadata
    status: PluginStatus = PluginStatus.INSTALLED
    permissions: List[PluginPermission] = Field(default_factory=list)
    capabilities: List[PluginCapability] = Field(default_factory=list)
    entrypoint: str = ""
    installed_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None


class ExecutionRequest(BaseModel):
    """Request to invoke a plugin capability."""

    request_id: str = Field(default_factory=lambda: f"req_{uuid4().hex[:10]}")
    plugin_id: str
    capability: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    agent_id: str = "system"
    mission_id: Optional[str] = None
    timeout_seconds: float = 30.0


class ExecutionResult(BaseModel):
    """Result of executing a plugin capability."""

    request_id: str
    plugin_id: str
    capability: str
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    execution_time_seconds: float = 0.0
    human_approved: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PluginMetrics(BaseModel):
    """Telemetry snapshot of plugin platform performance."""

    total_installed: int = 0
    total_loaded: int = 0
    total_enabled: int = 0
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    success_rate: float = 0.0
    average_duration_seconds: float = 0.0
    approvals_requested: int = 0
    approvals_granted: int = 0


class PluginHealth(BaseModel):
    """Composite health state of the plugin platform."""

    status: str = "healthy"
    components: Dict[str, str] = Field(default_factory=dict)
    total_plugins: int = 0
    active_capabilities: int = 0
