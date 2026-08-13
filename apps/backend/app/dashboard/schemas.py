"""Dashboard Pydantic Schemas Module.

Contains enterprise Pydantic v2 data models for Create, Update, Read, and Summary
operations across all dashboard entities, alongside high-level telemetry DTOs.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Generic, List, Optional, TypeVar
import uuid
from pydantic import BaseModel, ConfigDict, Field

from app.database.models.enums import (
    EventSeverity,
    HealthStatus,
    NotificationPriority,
    ResourceType,
)

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema enabling ORM mode compatibility for Pydantic v2."""

    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic unified paginated response wrapper for collection endpoints."""

    items: List[T] = Field(..., description="List of items for the requested page")
    page: int = Field(..., description="Current 1-indexed page number")
    page_size: int = Field(..., description="Number of items requested per page")
    total: int = Field(..., description="Total count of items matching the query")
    pages: int = Field(..., description="Total calculated pages available")


# ---------------------------------------------------------------------------
# 1. DashboardSnapshot Schemas
# ---------------------------------------------------------------------------

class DashboardSnapshotCreate(BaseModel):
    system_status: Dict[str, Any] = Field(default_factory=dict)
    resource_status: Dict[str, Any] = Field(default_factory=dict)
    active_agents: int = Field(default=0)
    active_models: int = Field(default=0)
    running_missions: int = Field(default=0)
    running_workflows: int = Field(default=0)
    voice_status: str = Field(default="idle")
    health_score: float = Field(default=1.0)


class DashboardSnapshotUpdate(BaseModel):
    system_status: Optional[Dict[str, Any]] = None
    resource_status: Optional[Dict[str, Any]] = None
    active_agents: Optional[int] = None
    active_models: Optional[int] = None
    running_missions: Optional[int] = None
    running_workflows: Optional[int] = None
    voice_status: Optional[str] = None
    health_score: Optional[float] = None


class DashboardSnapshotRead(BaseSchema):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    system_status: Dict[str, Any]
    resource_status: Dict[str, Any]
    active_agents: int
    active_models: int
    running_missions: int
    running_workflows: int
    voice_status: str
    health_score: float
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None


class DashboardSnapshotSummary(BaseSchema):
    id: uuid.UUID
    created_at: datetime
    health_score: float
    active_agents: int
    running_missions: int


# ---------------------------------------------------------------------------
# 2. SystemMetric Schemas
# ---------------------------------------------------------------------------

class SystemMetricCreate(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    hostname: str
    os_name: str
    cpu_usage: float
    cpu_temperature: Optional[float] = None
    memory_total: int
    memory_used: int
    memory_available: int
    swap_used: int = 0
    disk_total: int
    disk_used: int
    network_upload: int = 0
    network_download: int = 0
    uptime: float


class SystemMetricUpdate(BaseModel):
    cpu_usage: Optional[float] = None
    cpu_temperature: Optional[float] = None
    memory_used: Optional[int] = None
    memory_available: Optional[int] = None
    disk_used: Optional[int] = None
    network_upload: Optional[int] = None
    network_download: Optional[int] = None
    uptime: Optional[float] = None


class SystemMetricRead(BaseSchema):
    id: uuid.UUID
    timestamp: datetime
    hostname: str
    os_name: str
    cpu_usage: float
    cpu_temperature: Optional[float] = None
    memory_total: int
    memory_used: int
    memory_available: int
    swap_used: int
    disk_total: int
    disk_used: int
    network_upload: int
    network_download: int
    uptime: float


class SystemMetricSummary(BaseSchema):
    id: uuid.UUID
    timestamp: datetime
    hostname: str
    cpu_usage: float
    memory_used: int
    uptime: float


# ---------------------------------------------------------------------------
# 3. ResourceMetric Schemas
# ---------------------------------------------------------------------------

class ResourceMetricCreate(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resource_type: ResourceType = Field(default=ResourceType.CPU)
    resource_name: str
    current_value: float
    maximum_value: float
    percentage: float
    unit: str
    status: str = "normal"


class ResourceMetricUpdate(BaseModel):
    current_value: Optional[float] = None
    maximum_value: Optional[float] = None
    percentage: Optional[float] = None
    unit: Optional[str] = None
    status: Optional[str] = None


class ResourceMetricRead(BaseSchema):
    id: uuid.UUID
    timestamp: datetime
    resource_type: str
    resource_name: str
    current_value: float
    maximum_value: float
    percentage: float
    unit: str
    status: str


class ResourceMetricSummary(BaseSchema):
    id: uuid.UUID
    resource_type: str
    resource_name: str
    percentage: float
    status: str


# ---------------------------------------------------------------------------
# 4. GPUMetric Schemas
# ---------------------------------------------------------------------------

class GPUMetricCreate(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    gpu_name: str
    gpu_index: int
    temperature: float
    memory_total: int
    memory_used: int
    utilization: float
    power_usage: float
    fan_speed: float


class GPUMetricUpdate(BaseModel):
    temperature: Optional[float] = None
    memory_used: Optional[int] = None
    utilization: Optional[float] = None
    power_usage: Optional[float] = None
    fan_speed: Optional[float] = None


class GPUMetricRead(BaseSchema):
    id: uuid.UUID
    timestamp: datetime
    gpu_name: str
    gpu_index: int
    temperature: float
    memory_total: int
    memory_used: int
    utilization: float
    power_usage: float
    fan_speed: float


class GPUMetricSummary(BaseSchema):
    id: uuid.UUID
    gpu_index: int
    gpu_name: str
    temperature: float
    utilization: float


# ---------------------------------------------------------------------------
# 5. ProcessMetric Schemas
# ---------------------------------------------------------------------------

class ProcessMetricCreate(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    process_name: str
    pid: int
    cpu_percent: float
    memory_percent: float
    status: str


class ProcessMetricUpdate(BaseModel):
    cpu_percent: Optional[float] = None
    memory_percent: Optional[float] = None
    status: Optional[str] = None


class ProcessMetricRead(BaseSchema):
    id: uuid.UUID
    timestamp: datetime
    process_name: str
    pid: int
    cpu_percent: float
    memory_percent: float
    status: str


class ProcessMetricSummary(BaseSchema):
    id: uuid.UUID
    pid: int
    process_name: str
    cpu_percent: float
    memory_percent: float


# ---------------------------------------------------------------------------
# 6. DashboardEvent Schemas
# ---------------------------------------------------------------------------

class DashboardEventCreate(BaseModel):
    snapshot_id: Optional[uuid.UUID] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: str
    severity: EventSeverity = Field(default=EventSeverity.INFO)
    source: str
    title: str
    description: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class DashboardEventUpdate(BaseModel):
    severity: Optional[EventSeverity] = None
    title: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    resolved: Optional[bool] = None
    resolved_at: Optional[datetime] = None


class DashboardEventRead(BaseSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    snapshot_id: Optional[uuid.UUID] = None
    timestamp: datetime
    event_type: str
    severity: str
    source: str
    title: str
    description: str
    event_metadata: Dict[str, Any] = Field(default_factory=dict, serialization_alias="metadata")
    resolved: bool
    resolved_at: Optional[datetime] = None


class DashboardEventSummary(BaseSchema):
    id: uuid.UUID
    timestamp: datetime
    event_type: str
    severity: str
    title: str
    resolved: bool


# ---------------------------------------------------------------------------
# 7. DashboardNotification Schemas
# ---------------------------------------------------------------------------

class DashboardNotificationCreate(BaseModel):
    snapshot_id: Optional[uuid.UUID] = None
    type: str
    priority: NotificationPriority = Field(default=NotificationPriority.NORMAL)
    title: str
    message: str
    read: bool = False
    read_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class DashboardNotificationUpdate(BaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    read: Optional[bool] = None
    read_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class DashboardNotificationRead(BaseSchema):
    id: uuid.UUID
    snapshot_id: Optional[uuid.UUID] = None
    created_at: datetime
    type: str
    priority: str
    title: str
    message: str
    read: bool
    read_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class DashboardNotificationSummary(BaseSchema):
    id: uuid.UUID
    created_at: datetime
    priority: str
    title: str
    read: bool


# ---------------------------------------------------------------------------
# 8. AnalyticsRecord Schemas
# ---------------------------------------------------------------------------

class AnalyticsRecordCreate(BaseModel):
    snapshot_id: Optional[uuid.UUID] = None
    metric_name: str
    metric_value: float
    metric_type: str
    aggregation_period: str
    labels: Dict[str, Any] = Field(default_factory=dict)


class AnalyticsRecordUpdate(BaseModel):
    metric_value: Optional[float] = None
    metric_type: Optional[str] = None
    aggregation_period: Optional[str] = None
    labels: Optional[Dict[str, Any]] = None


class AnalyticsRecordRead(BaseSchema):
    id: uuid.UUID
    snapshot_id: Optional[uuid.UUID] = None
    created_at: datetime
    metric_name: str
    metric_value: float
    metric_type: str
    aggregation_period: str
    labels: Dict[str, Any]


class AnalyticsRecordSummary(BaseSchema):
    id: uuid.UUID
    metric_name: str
    metric_value: float
    aggregation_period: str


# ---------------------------------------------------------------------------
# 9. HealthRecord Schemas
# ---------------------------------------------------------------------------

class HealthRecordCreate(BaseModel):
    snapshot_id: Optional[uuid.UUID] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    component: str
    status: HealthStatus = Field(default=HealthStatus.HEALTHY)
    latency: float = 0.0
    response_time: float = 0.0
    details: Dict[str, Any] = Field(default_factory=dict)


class HealthRecordUpdate(BaseModel):
    status: Optional[HealthStatus] = None
    latency: Optional[float] = None
    response_time: Optional[float] = None
    details: Optional[Dict[str, Any]] = None


class HealthRecordRead(BaseSchema):
    id: uuid.UUID
    snapshot_id: Optional[uuid.UUID] = None
    timestamp: datetime
    component: str
    status: str
    latency: float
    response_time: float
    details: Dict[str, Any]


class HealthRecordSummary(BaseSchema):
    id: uuid.UUID
    timestamp: datetime
    component: str
    status: str
    latency: float


# ---------------------------------------------------------------------------
# 10. DashboardConfiguration Schemas
# ---------------------------------------------------------------------------

class DashboardConfigurationCreate(BaseModel):
    refresh_interval: int = 5
    cache_ttl: int = 60
    heartbeat_interval: int = 15
    metrics_interval: int = 10
    max_connections: int = 1000
    max_notifications: int = 500
    retention_days: int = 30


class DashboardConfigurationUpdate(BaseModel):
    refresh_interval: Optional[int] = None
    cache_ttl: Optional[int] = None
    heartbeat_interval: Optional[int] = None
    metrics_interval: Optional[int] = None
    max_connections: Optional[int] = None
    max_notifications: Optional[int] = None
    retention_days: Optional[int] = None


class DashboardConfigurationRead(BaseSchema):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    refresh_interval: int
    cache_ttl: int
    heartbeat_interval: int
    metrics_interval: int
    max_connections: int
    max_notifications: int
    retention_days: int


class DashboardConfigurationSummary(BaseSchema):
    id: uuid.UUID
    refresh_interval: int
    cache_ttl: int
    retention_days: int


# ---------------------------------------------------------------------------
# High-Level Consolidated Dashboard DTOs (from Phase M3.4.22.1)
# ---------------------------------------------------------------------------

class SystemStatus(BaseModel):
    status: str = Field(..., description="Overall system health status string")
    uptime_seconds: float = Field(..., description="System total uptime duration in seconds")
    active_nodes: int = Field(default=0, description="Count of active cluster compute nodes")
    cpu_usage_percent: float = Field(default=0.0, description="Current cluster CPU usage percentage")
    memory_usage_percent: float = Field(default=0.0, description="Current cluster Memory usage percentage")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional status metadata")


class ResourceStatus(BaseModel):
    cpu_cores_total: int = Field(..., description="Total available CPU core count")
    cpu_cores_used: float = Field(..., description="Allocated/used CPU cores count")
    memory_total_bytes: int = Field(..., description="Total installed RAM bytes")
    memory_used_bytes: int = Field(..., description="Currently consumed RAM bytes")
    disk_total_bytes: int = Field(..., description="Total storage capacity in bytes")
    disk_used_bytes: int = Field(..., description="Consumed storage capacity in bytes")
    gpu_count: int = Field(default=0, description="Total active GPU devices attached")
    gpu_memory_used_bytes: Optional[int] = Field(default=None, description="Consumed VRAM in bytes")


class MissionSummary(BaseModel):
    total_missions: int = Field(default=0, description="Total recorded missions")
    active_missions: int = Field(default=0, description="Missions currently running")
    completed_missions: int = Field(default=0, description="Successfully finished missions")
    failed_missions: int = Field(default=0, description="Failed mission executions count")
    pending_missions: int = Field(default=0, description="Missions queued awaiting execution")


class AgentSummary(BaseModel):
    total_agents: int = Field(default=0, description="Total registered workforce agents")
    idle_agents: int = Field(default=0, description="Agents ready for assignment")
    busy_agents: int = Field(default=0, description="Agents currently executing tasks")
    error_agents: int = Field(default=0, description="Agents in errored state")


class NotificationSummary(BaseModel):
    unread_count: int = Field(default=0, description="Count of unread dashboard alerts")
    critical_alerts: int = Field(default=0, description="Count of active critical-severity alerts")
    warning_alerts: int = Field(default=0, description="Count of active warning-severity alerts")
    info_alerts: int = Field(default=0, description="Count of informational notifications")


class AnalyticsSummary(BaseModel):
    total_requests: int = Field(default=0, description="Total API requests processed")
    avg_latency_ms: float = Field(default=0.0, description="Average API latency in milliseconds")
    error_rate_percent: float = Field(default=0.0, description="API error rate percentage")
    token_usage_total: int = Field(default=0, description="Total LLM tokens consumed")


class HealthSummary(BaseModel):
    is_healthy: bool = Field(..., description="Overall health state boolean")
    database_status: str = Field(default="unknown", description="Database subsystem connectivity state")
    cache_status: str = Field(default="unknown", description="Cache subsystem operational state")
    message_bus_status: str = Field(default="unknown", description="Event bus operational state")
    checks: Dict[str, Any] = Field(default_factory=dict, description="Detailed subsystem health checks")


class DashboardOverview(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Telemetry snapshot creation UTC timestamp")
    system: SystemStatus = Field(..., description="System status details")
    resources: ResourceStatus = Field(..., description="Resource utilization metrics")
    missions: MissionSummary = Field(..., description="Mission workforce metrics")
    agents: AgentSummary = Field(..., description="Agent workforce summary")
    notifications: NotificationSummary = Field(..., description="Alert and notification counters")
    analytics: AnalyticsSummary = Field(..., description="API and LLM analytics summary")
    health: HealthSummary = Field(..., description="Subsystem health diagnostics")
