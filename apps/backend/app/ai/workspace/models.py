"""Pydantic data models, enums, and schemas for Enterprise Workspace & Remote AI Orchestration Platform.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import time
import uuid


class WorkspaceType(str, Enum):
    """Enumerate workspace environment categories."""

    PERSONAL = "personal"
    DEVELOPER = "developer"
    RESEARCH = "research"
    ORGANIZATION = "organization"
    EDUCATION = "education"
    ENTERPRISE = "enterprise"


class MemberRole(str, Enum):
    """Enumerate workspace member role permissions."""

    ADMIN = "admin"
    LEAD = "lead"
    DEVELOPER = "developer"
    RESEARCHER = "researcher"
    VIEWER = "viewer"


class DeviceStatus(str, Enum):
    """Enumerate remote node device statuses."""

    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"


class SyncStatus(str, Enum):
    """Enumerate delta sync statuses."""

    SYNCED = "synced"
    SYNCING = "syncing"
    CONFLICT = "conflict"
    ERROR = "error"


class WorkspaceMember(BaseModel):
    """Workspace team member payload."""

    member_id: str = Field(default_factory=lambda: f"mem_{uuid.uuid4().hex[:8]}")
    name: str = Field(...)
    email: str = Field(...)
    role: MemberRole = Field(MemberRole.DEVELOPER)
    joined_at: float = Field(default_factory=time.time)


class WorkspaceDevice(BaseModel):
    """Remote node machine device payload."""

    device_id: str = Field(default_factory=lambda: f"dev_{uuid.uuid4().hex[:8]}")
    name: str = Field(...)
    device_type: str = Field("desktop_pc")
    ip_address: str = Field("192.168.1.100")
    status: DeviceStatus = Field(DeviceStatus.ONLINE)
    last_seen: float = Field(default_factory=time.time)


class WorkspaceDefinition(BaseModel):
    """Complete workspace definition payload."""

    workspace_id: str = Field(default_factory=lambda: f"ws_{uuid.uuid4().hex[:8]}")
    name: str = Field(...)
    workspace_type: WorkspaceType = Field(WorkspaceType.PERSONAL)
    description: str = Field("Enterprise collaborative workspace")
    members: List[WorkspaceMember] = Field(default_factory=list)
    devices: List[WorkspaceDevice] = Field(default_factory=list)
    created_at: float = Field(default_factory=time.time)


class RemoteExecutionRequest(BaseModel):
    """Payload for remote desktop/browser automation or model execution."""

    request_id: str = Field(default_factory=lambda: f"req_{uuid.uuid4().hex[:8]}")
    target_device_id: str = Field(...)
    command_type: str = Field("desktop_automation")
    payload: Dict[str, Any] = Field(default_factory=dict)
    timeout_sec: float = Field(60.0)


class RemoteExecutionResult(BaseModel):
    """Execution result returned from remote node machine."""

    execution_id: str = Field(default_factory=lambda: f"exec_{uuid.uuid4().hex[:8]}")
    request_id: str = Field(...)
    success: bool = Field(True)
    output: Any = Field(None)
    error_message: Optional[str] = Field(None)
    duration_sec: float = Field(0.0)
    timestamp: float = Field(default_factory=time.time)


class WorkspaceSearchResult(BaseModel):
    """Unified search query result across workspace artifacts."""

    query: str = Field(...)
    total_results: int = Field(0)
    items: List[Dict[str, Any]] = Field(default_factory=list)
    timestamp: float = Field(default_factory=time.time)


class WorkspaceHealth(BaseModel):
    """Health monitor status model."""

    is_healthy: bool = Field(True)
    total_workspaces_count: int = Field(0)
    active_members_count: int = Field(0)
    active_devices_count: int = Field(0)
    timestamp: float = Field(default_factory=time.time)


class WorkspaceMetrics(BaseModel):
    """Telemetry collector metrics model."""

    total_workspaces: int = Field(0)
    total_members: int = Field(0)
    remote_executions: int = Field(0)
    sync_operations: int = Field(0)
    timestamp: float = Field(default_factory=time.time)
