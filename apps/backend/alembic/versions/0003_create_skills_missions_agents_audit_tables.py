"""Create skills, missions, agents, and audit events persistence tables and indexes.

Revision ID: 0003_create_skills_missions_agents_audit_tables
Revises: 0002_create_dashboard_tables
Create Date: 2026-08-15

Creates tables, foreign key constraints, and indexes for:
- skills
- skill_versions
- missions
- mission_tasks
- agents
- agent_executions
- audit_events
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0003_create_skills_missions_agents_audit_tables"
down_revision: Union[str, None] = "0002_create_dashboard_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create skills table
    op.create_table(
        "skills",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("purpose", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False, server_default="general"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.9"),
        sa.Column("success_rate", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("usage_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("owner", sa.String(length=100), nullable=False, server_default="NovaUser"),
        sa.Column("source", sa.String(length=50), nullable=False, server_default="user_taught"),
        sa.Column("trigger_patterns_json", sa.JSON(), nullable=False),
        sa.Column("required_tools_json", sa.JSON(), nullable=False),
        sa.Column("variables_json", sa.JSON(), nullable=False),
        sa.Column("steps_json", sa.JSON(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_skills_id"), "skills", ["id"], unique=False)
    op.create_index(op.f("ix_skills_name"), "skills", ["name"], unique=False)
    op.create_index(op.f("ix_skills_category"), "skills", ["category"], unique=False)
    op.create_index(op.f("ix_skills_status"), "skills", ["status"], unique=False)

    # 2. Create skill_versions table
    op.create_table(
        "skill_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("skill_id", sa.Uuid(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("changes", sa.Text(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("steps_snapshot_json", sa.JSON(), nullable=False),
        sa.Column("success_rate_snapshot", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_skill_versions_id"), "skill_versions", ["id"], unique=False)
    op.create_index(op.f("ix_skill_versions_skill_id"), "skill_versions", ["skill_id"], unique=False)

    # 3. Create missions table
    op.create_table(
        "missions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("goal", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False, server_default="automation"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="PENDING"),
        sa.Column("progress_percent", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("assigned_agent", sa.String(length=100), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_missions_id"), "missions", ["id"], unique=False)
    op.create_index(op.f("ix_missions_title"), "missions", ["title"], unique=False)
    op.create_index(op.f("ix_missions_category"), "missions", ["category"], unique=False)
    op.create_index(op.f("ix_missions_status"), "missions", ["status"], unique=False)

    # 4. Create mission_tasks table
    op.create_table(
        "mission_tasks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("mission_id", sa.Uuid(), nullable=False),
        sa.Column("task_order", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="PENDING"),
        sa.Column("assigned_agent", sa.String(length=100), nullable=True),
        sa.Column("dependencies_json", sa.JSON(), nullable=False),
        sa.Column("output_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["mission_id"], ["missions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_mission_tasks_id"), "mission_tasks", ["id"], unique=False)
    op.create_index(op.f("ix_mission_tasks_mission_id"), "mission_tasks", ["mission_id"], unique=False)
    op.create_index(op.f("ix_mission_tasks_status"), "mission_tasks", ["status"], unique=False)

    # 5. Create agents table
    op.create_table(
        "agents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("role", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="IDLE"),
        sa.Column("capabilities_json", sa.JSON(), nullable=False),
        sa.Column("performance_score", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("tasks_completed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_agents_id"), "agents", ["id"], unique=False)
    op.create_index(op.f("ix_agents_name"), "agents", ["name"], unique=False)
    op.create_index(op.f("ix_agents_role"), "agents", ["role"], unique=False)
    op.create_index(op.f("ix_agents_status"), "agents", ["status"], unique=False)

    # 6. Create agent_executions table
    op.create_table(
        "agent_executions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("agent_id", sa.Uuid(), nullable=False),
        sa.Column("goal_text", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="COMPLETED"),
        sa.Column("duration_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("result_summary", sa.Text(), nullable=True),
        sa.Column("logs_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_agent_executions_id"), "agent_executions", ["id"], unique=False)
    op.create_index(op.f("ix_agent_executions_agent_id"), "agent_executions", ["agent_id"], unique=False)

    # 7. Create audit_events table
    op.create_table(
        "audit_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("action", sa.String(length=150), nullable=False),
        sa.Column("tool_name", sa.String(length=150), nullable=True),
        sa.Column("risk_level", sa.String(length=20), nullable=False, server_default="SAFE"),
        sa.Column("actor", sa.String(length=100), nullable=False, server_default="User"),
        sa.Column("decision", sa.String(length=30), nullable=False, server_default="ALLOWED"),
        sa.Column("details_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_events_id"), "audit_events", ["id"], unique=False)
    op.create_index(op.f("ix_audit_events_event_type"), "audit_events", ["event_type"], unique=False)
    op.create_index(op.f("ix_audit_events_action"), "audit_events", ["action"], unique=False)
    op.create_index(op.f("ix_audit_events_tool_name"), "audit_events", ["tool_name"], unique=False)
    op.create_index(op.f("ix_audit_events_risk_level"), "audit_events", ["risk_level"], unique=False)


def downgrade() -> None:
    op.drop_table("audit_events")
    op.drop_table("agent_executions")
    op.drop_table("agents")
    op.drop_table("mission_tasks")
    op.drop_table("missions")
    op.drop_table("skill_versions")
    op.drop_table("skills")
