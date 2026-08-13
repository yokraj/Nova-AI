"""Create dashboard persistence tables and indexes.

Revision ID: 0002_create_dashboard_tables
Revises: 0001_create_initial_tables
Create Date: 2026-08-02

Creates tables, foreign key constraints, and indexes for:
- dashboard_snapshots
- system_metrics
- resource_metrics
- gpu_metrics
- process_metrics
- dashboard_events
- dashboard_notifications
- analytics_records
- health_records
- dashboard_configurations
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0002_create_dashboard_tables"
down_revision: Union[str, None] = "0001_create_initial_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create dashboard_snapshots
    op.create_table(
        "dashboard_snapshots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("system_status", sa.JSON(), nullable=False),
        sa.Column("resource_status", sa.JSON(), nullable=False),
        sa.Column("active_agents", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("active_models", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("running_missions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("running_workflows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("voice_status", sa.String(length=50), nullable=False, server_default="idle"),
        sa.Column("health_score", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_dashboard_snapshots_created_at"),
        "dashboard_snapshots",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_dashboard_snapshots_id"),
        "dashboard_snapshots",
        ["id"],
        unique=False,
    )

    # 2. Create system_metrics
    op.create_table(
        "system_metrics",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("hostname", sa.String(length=255), nullable=False),
        sa.Column("os_name", sa.String(length=100), nullable=False),
        sa.Column("cpu_usage", sa.Float(), nullable=False),
        sa.Column("cpu_temperature", sa.Float(), nullable=True),
        sa.Column("memory_total", sa.BigInteger(), nullable=False),
        sa.Column("memory_used", sa.BigInteger(), nullable=False),
        sa.Column("memory_available", sa.BigInteger(), nullable=False),
        sa.Column("swap_used", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("disk_total", sa.BigInteger(), nullable=False),
        sa.Column("disk_used", sa.BigInteger(), nullable=False),
        sa.Column("network_upload", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("network_download", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("uptime", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_system_metrics_hostname"),
        "system_metrics",
        ["hostname"],
        unique=False,
    )
    op.create_index(
        op.f("ix_system_metrics_id"),
        "system_metrics",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_system_metrics_timestamp"),
        "system_metrics",
        ["timestamp"],
        unique=False,
    )

    # 3. Create resource_metrics
    op.create_table(
        "resource_metrics",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resource_type", sa.String(length=50), nullable=False),
        sa.Column("resource_name", sa.String(length=255), nullable=False),
        sa.Column("current_value", sa.Float(), nullable=False),
        sa.Column("maximum_value", sa.Float(), nullable=False),
        sa.Column("percentage", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_resource_metrics_id"),
        "resource_metrics",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_resource_metrics_resource_name"),
        "resource_metrics",
        ["resource_name"],
        unique=False,
    )
    op.create_index(
        op.f("ix_resource_metrics_resource_type"),
        "resource_metrics",
        ["resource_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_resource_metrics_status"),
        "resource_metrics",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_resource_metrics_timestamp"),
        "resource_metrics",
        ["timestamp"],
        unique=False,
    )

    # 4. Create gpu_metrics
    op.create_table(
        "gpu_metrics",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("gpu_name", sa.String(length=255), nullable=False),
        sa.Column("gpu_index", sa.Integer(), nullable=False),
        sa.Column("temperature", sa.Float(), nullable=False),
        sa.Column("memory_total", sa.BigInteger(), nullable=False),
        sa.Column("memory_used", sa.BigInteger(), nullable=False),
        sa.Column("utilization", sa.Float(), nullable=False),
        sa.Column("power_usage", sa.Float(), nullable=False),
        sa.Column("fan_speed", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_gpu_metrics_gpu_index"),
        "gpu_metrics",
        ["gpu_index"],
        unique=False,
    )
    op.create_index(
        op.f("ix_gpu_metrics_id"),
        "gpu_metrics",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_gpu_metrics_timestamp"),
        "gpu_metrics",
        ["timestamp"],
        unique=False,
    )

    # 5. Create process_metrics
    op.create_table(
        "process_metrics",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("process_name", sa.String(length=255), nullable=False),
        sa.Column("pid", sa.Integer(), nullable=False),
        sa.Column("cpu_percent", sa.Float(), nullable=False),
        sa.Column("memory_percent", sa.Float(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_process_metrics_id"),
        "process_metrics",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_process_metrics_process_name"),
        "process_metrics",
        ["process_name"],
        unique=False,
    )
    op.create_index(
        op.f("ix_process_metrics_status"),
        "process_metrics",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_process_metrics_timestamp"),
        "process_metrics",
        ["timestamp"],
        unique=False,
    )

    # 6. Create dashboard_events
    op.create_table(
        "dashboard_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("snapshot_id", sa.Uuid(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("severity", sa.String(length=50), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("resolved", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["snapshot_id"], ["dashboard_snapshots.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_dashboard_events_event_type"),
        "dashboard_events",
        ["event_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_dashboard_events_id"),
        "dashboard_events",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_dashboard_events_severity"),
        "dashboard_events",
        ["severity"],
        unique=False,
    )
    op.create_index(
        op.f("ix_dashboard_events_snapshot_id"),
        "dashboard_events",
        ["snapshot_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_dashboard_events_timestamp"),
        "dashboard_events",
        ["timestamp"],
        unique=False,
    )

    # 7. Create dashboard_notifications
    op.create_table(
        "dashboard_notifications",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("snapshot_id", sa.Uuid(), nullable=True),
        sa.Column("type", sa.String(length=100), nullable=False),
        sa.Column("priority", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("read", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["snapshot_id"], ["dashboard_snapshots.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_dashboard_notifications_created_at"),
        "dashboard_notifications",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_dashboard_notifications_id"),
        "dashboard_notifications",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_dashboard_notifications_priority"),
        "dashboard_notifications",
        ["priority"],
        unique=False,
    )
    op.create_index(
        op.f("ix_dashboard_notifications_snapshot_id"),
        "dashboard_notifications",
        ["snapshot_id"],
        unique=False,
    )

    # 8. Create analytics_records
    op.create_table(
        "analytics_records",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("snapshot_id", sa.Uuid(), nullable=True),
        sa.Column("metric_name", sa.String(length=255), nullable=False),
        sa.Column("metric_value", sa.Float(), nullable=False),
        sa.Column("metric_type", sa.String(length=100), nullable=False),
        sa.Column("aggregation_period", sa.String(length=50), nullable=False),
        sa.Column("labels", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["snapshot_id"], ["dashboard_snapshots.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_analytics_records_created_at"),
        "analytics_records",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analytics_records_id"),
        "analytics_records",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analytics_records_metric_name"),
        "analytics_records",
        ["metric_name"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analytics_records_snapshot_id"),
        "analytics_records",
        ["snapshot_id"],
        unique=False,
    )

    # 9. Create health_records
    op.create_table(
        "health_records",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("snapshot_id", sa.Uuid(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("component", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("latency", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("response_time", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["snapshot_id"], ["dashboard_snapshots.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_health_records_id"),
        "health_records",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_health_records_snapshot_id"),
        "health_records",
        ["snapshot_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_health_records_status"),
        "health_records",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_health_records_timestamp"),
        "health_records",
        ["timestamp"],
        unique=False,
    )

    # 10. Create dashboard_configurations
    op.create_table(
        "dashboard_configurations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("refresh_interval", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("cache_ttl", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("heartbeat_interval", sa.Integer(), nullable=False, server_default="15"),
        sa.Column("metrics_interval", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("max_connections", sa.Integer(), nullable=False, server_default="1000"),
        sa.Column("max_notifications", sa.Integer(), nullable=False, server_default="500"),
        sa.Column("retention_days", sa.Integer(), nullable=False, server_default="30"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_dashboard_configurations_created_at"),
        "dashboard_configurations",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_dashboard_configurations_id"),
        "dashboard_configurations",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_dashboard_configurations_id"), table_name="dashboard_configurations")
    op.drop_index(op.f("ix_dashboard_configurations_created_at"), table_name="dashboard_configurations")
    op.drop_table("dashboard_configurations")

    op.drop_index(op.f("ix_health_records_timestamp"), table_name="health_records")
    op.drop_index(op.f("ix_health_records_status"), table_name="health_records")
    op.drop_index(op.f("ix_health_records_snapshot_id"), table_name="health_records")
    op.drop_index(op.f("ix_health_records_id"), table_name="health_records")
    op.drop_table("health_records")

    op.drop_index(op.f("ix_analytics_records_snapshot_id"), table_name="analytics_records")
    op.drop_index(op.f("ix_analytics_records_metric_name"), table_name="analytics_records")
    op.drop_index(op.f("ix_analytics_records_id"), table_name="analytics_records")
    op.drop_index(op.f("ix_analytics_records_created_at"), table_name="analytics_records")
    op.drop_table("analytics_records")

    op.drop_index(op.f("ix_dashboard_notifications_snapshot_id"), table_name="dashboard_notifications")
    op.drop_index(op.f("ix_dashboard_notifications_priority"), table_name="dashboard_notifications")
    op.drop_index(op.f("ix_dashboard_notifications_id"), table_name="dashboard_notifications")
    op.drop_index(op.f("ix_dashboard_notifications_created_at"), table_name="dashboard_notifications")
    op.drop_table("dashboard_notifications")

    op.drop_index(op.f("ix_dashboard_events_timestamp"), table_name="dashboard_events")
    op.drop_index(op.f("ix_dashboard_events_snapshot_id"), table_name="dashboard_events")
    op.drop_index(op.f("ix_dashboard_events_severity"), table_name="dashboard_events")
    op.drop_index(op.f("ix_dashboard_events_id"), table_name="dashboard_events")
    op.drop_index(op.f("ix_dashboard_events_event_type"), table_name="dashboard_events")
    op.drop_table("dashboard_events")

    op.drop_index(op.f("ix_process_metrics_timestamp"), table_name="process_metrics")
    op.drop_index(op.f("ix_process_metrics_status"), table_name="process_metrics")
    op.drop_index(op.f("ix_process_metrics_process_name"), table_name="process_metrics")
    op.drop_index(op.f("ix_process_metrics_id"), table_name="process_metrics")
    op.drop_table("process_metrics")

    op.drop_index(op.f("ix_gpu_metrics_timestamp"), table_name="gpu_metrics")
    op.drop_index(op.f("ix_gpu_metrics_id"), table_name="gpu_metrics")
    op.drop_index(op.f("ix_gpu_metrics_gpu_index"), table_name="gpu_metrics")
    op.drop_table("gpu_metrics")

    op.drop_index(op.f("ix_resource_metrics_timestamp"), table_name="resource_metrics")
    op.drop_index(op.f("ix_resource_metrics_status"), table_name="resource_metrics")
    op.drop_index(op.f("ix_resource_metrics_resource_type"), table_name="resource_metrics")
    op.drop_index(op.f("ix_resource_metrics_resource_name"), table_name="resource_metrics")
    op.drop_index(op.f("ix_resource_metrics_id"), table_name="resource_metrics")
    op.drop_table("resource_metrics")

    op.drop_index(op.f("ix_system_metrics_timestamp"), table_name="system_metrics")
    op.drop_index(op.f("ix_system_metrics_id"), table_name="system_metrics")
    op.drop_index(op.f("ix_system_metrics_hostname"), table_name="system_metrics")
    op.drop_table("system_metrics")

    op.drop_index(op.f("ix_dashboard_snapshots_id"), table_name="dashboard_snapshots")
    op.drop_index(op.f("ix_dashboard_snapshots_created_at"), table_name="dashboard_snapshots")
    op.drop_table("dashboard_snapshots")
