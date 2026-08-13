"""SQLAlchemy 2.x Database Models for Nova AI Enterprise Dashboard.

Defines persistence schemas for periodic snapshots, node telemetry, hardware resource
metrics, GPU utilization, process states, events, alerts/notifications, analytics,
component health diagnostics, and dashboard configurations.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import BaseEntity
from app.database.models.enums import (
    EventSeverity,
    HealthStatus,
    NotificationPriority,
    ResourceType,
)


class DashboardSnapshot(BaseEntity):
    """Stores periodic consolidated dashboard state snapshots."""

    __tablename__ = "dashboard_snapshots"

    system_status: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    resource_status: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    active_agents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    active_models: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    running_missions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    running_workflows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    voice_status: Mapped[str] = mapped_column(String(50), default="idle", nullable=False)
    health_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    # Soft-delete support
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships (One-to-Many)
    events = relationship(
        "DashboardEvent", back_populates="snapshot", cascade="all, delete-orphan"
    )
    notifications = relationship(
        "DashboardNotification", back_populates="snapshot", cascade="all, delete-orphan"
    )
    analytics_records = relationship(
        "AnalyticsRecord", back_populates="snapshot", cascade="all, delete-orphan"
    )
    health_records = relationship(
        "HealthRecord", back_populates="snapshot", cascade="all, delete-orphan"
    )


class SystemMetric(BaseEntity):
    """Tracks OS and compute node telemetry metrics over time."""

    __tablename__ = "system_metrics"

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False,
    )
    hostname: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    os_name: Mapped[str] = mapped_column(String(100), nullable=False)
    cpu_usage: Mapped[float] = mapped_column(Float, nullable=False)
    cpu_temperature: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    memory_total: Mapped[int] = mapped_column(BigInteger, nullable=False)
    memory_used: Mapped[int] = mapped_column(BigInteger, nullable=False)
    memory_available: Mapped[int] = mapped_column(BigInteger, nullable=False)
    swap_used: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    disk_total: Mapped[int] = mapped_column(BigInteger, nullable=False)
    disk_used: Mapped[int] = mapped_column(BigInteger, nullable=False)
    network_upload: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    network_download: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    uptime: Mapped[float] = mapped_column(Float, nullable=False)


class ResourceMetric(BaseEntity):
    """Tracks individual hardware resource utilization (CPU, RAM, Disk, Network, GPU)."""

    __tablename__ = "resource_metrics"

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False,
    )
    resource_type: Mapped[str] = mapped_column(
        String(50), default=ResourceType.CPU.value, index=True, nullable=False
    )
    resource_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    current_value: Mapped[float] = mapped_column(Float, nullable=False)
    maximum_value: Mapped[float] = mapped_column(Float, nullable=False)
    percentage: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), index=True, default="normal", nullable=False)


class GPUMetric(BaseEntity):
    """Tracks attached GPU accelerator telemetry, VRAM usage, and power."""

    __tablename__ = "gpu_metrics"

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False,
    )
    gpu_name: Mapped[str] = mapped_column(String(255), nullable=False)
    gpu_index: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    memory_total: Mapped[int] = mapped_column(BigInteger, nullable=False)
    memory_used: Mapped[int] = mapped_column(BigInteger, nullable=False)
    utilization: Mapped[float] = mapped_column(Float, nullable=False)
    power_usage: Mapped[float] = mapped_column(Float, nullable=False)
    fan_speed: Mapped[float] = mapped_column(Float, nullable=False)


class ProcessMetric(BaseEntity):
    """Tracks system and agent worker process table metrics."""

    __tablename__ = "process_metrics"

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False,
    )
    process_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    pid: Mapped[int] = mapped_column(Integer, nullable=False)
    cpu_percent: Mapped[float] = mapped_column(Float, nullable=False)
    memory_percent: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(50), index=True, nullable=False)


class DashboardEvent(BaseEntity):
    """Stores system events, warnings, errors, and audit logs for dashboard view."""

    __tablename__ = "dashboard_events"

    snapshot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("dashboard_snapshots.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    severity: Mapped[str] = mapped_column(
        String(50), default=EventSeverity.INFO.value, index=True, nullable=False
    )
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    event_metadata: Mapped[Dict[str, Any]] = mapped_column(
        "metadata", JSON, default=dict, nullable=False
    )
    resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationship
    snapshot = relationship("DashboardSnapshot", back_populates="events")


class DashboardNotification(BaseEntity):
    """Stores system notifications and alert payloads."""

    __tablename__ = "dashboard_notifications"

    snapshot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("dashboard_snapshots.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    priority: Mapped[str] = mapped_column(
        String(50), default=NotificationPriority.NORMAL.value, index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationship
    snapshot = relationship("DashboardSnapshot", back_populates="notifications")


class AnalyticsRecord(BaseEntity):
    """Stores aggregated API, LLM token, and performance analytics records."""

    __tablename__ = "analytics_records"

    snapshot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("dashboard_snapshots.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    metric_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    metric_type: Mapped[str] = mapped_column(String(100), nullable=False)
    aggregation_period: Mapped[str] = mapped_column(String(50), nullable=False)
    labels: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    # Relationship
    snapshot = relationship("DashboardSnapshot", back_populates="analytics_records")


class HealthRecord(BaseEntity):
    """Stores diagnostic health status checks per component."""

    __tablename__ = "health_records"

    snapshot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("dashboard_snapshots.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False,
    )
    component: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), default=HealthStatus.HEALTHY.value, index=True, nullable=False
    )
    latency: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    response_time: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    details: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    # Relationship
    snapshot = relationship("DashboardSnapshot", back_populates="health_records")


class DashboardConfiguration(BaseEntity):
    """Stores dashboard system parameters, refresh rates, and memory buffer retention limits."""

    __tablename__ = "dashboard_configurations"

    refresh_interval: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    cache_ttl: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    heartbeat_interval: Mapped[int] = mapped_column(Integer, default=15, nullable=False)
    metrics_interval: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    max_connections: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)
    max_notifications: Mapped[int] = mapped_column(Integer, default=500, nullable=False)
    retention_days: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
