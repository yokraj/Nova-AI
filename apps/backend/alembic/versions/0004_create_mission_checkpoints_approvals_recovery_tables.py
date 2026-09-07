"""Create mission checkpoints, approvals, and recovery events persistence tables.

Revision ID: 0004_create_mission_checkpoints_approvals_recovery_tables
Revises: 0003_create_skills_missions_agents_audit_tables
Create Date: 2026-08-15

Creates tables, foreign key constraints, and indexes for:
- mission_checkpoints
- mission_approvals
- mission_recovery_events
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0004_create_mission_checkpoints_approvals_recovery_tables"
down_revision: Union[str, None] = "0003_create_skills_missions_agents_audit_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create mission_checkpoints table
    op.create_table(
        "mission_checkpoints",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("mission_id", sa.Uuid(), nullable=False),
        sa.Column("execution_id", sa.String(length=100), nullable=False),
        sa.Column("checkpoint_id", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="EXECUTING"),
        sa.Column("current_step", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completed_steps_json", sa.JSON(), nullable=False),
        sa.Column("pending_steps_json", sa.JSON(), nullable=False),
        sa.Column("retry_counters_json", sa.JSON(), nullable=False),
        sa.Column("budget_state_json", sa.JSON(), nullable=False),
        sa.Column("approval_state_json", sa.JSON(), nullable=False),
        sa.Column("verification_results_json", sa.JSON(), nullable=False),
        sa.Column("checkpoint_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_safe_resumable", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["mission_id"], ["missions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_mission_checkpoints_id"), "mission_checkpoints", ["id"], unique=False)
    op.create_index(op.f("ix_mission_checkpoints_mission_id"), "mission_checkpoints", ["mission_id"], unique=False)
    op.create_index(op.f("ix_mission_checkpoints_execution_id"), "mission_checkpoints", ["execution_id"], unique=False)
    op.create_index(op.f("ix_mission_checkpoints_checkpoint_id"), "mission_checkpoints", ["checkpoint_id"], unique=False)
    op.create_index(op.f("ix_mission_checkpoints_status"), "mission_checkpoints", ["status"], unique=False)

    # 2. Create mission_approvals table
    op.create_table(
        "mission_approvals",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("mission_id", sa.Uuid(), nullable=False),
        sa.Column("step_id", sa.String(length=100), nullable=False),
        sa.Column("tool_name", sa.String(length=100), nullable=False),
        sa.Column("risk_level", sa.String(length=30), nullable=False, server_default="HIGH"),
        sa.Column("target_details_json", sa.JSON(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="PENDING"),
        sa.Column("authorized_by", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["mission_id"], ["missions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_mission_approvals_id"), "mission_approvals", ["id"], unique=False)
    op.create_index(op.f("ix_mission_approvals_mission_id"), "mission_approvals", ["mission_id"], unique=False)
    op.create_index(op.f("ix_mission_approvals_step_id"), "mission_approvals", ["step_id"], unique=False)
    op.create_index(op.f("ix_mission_approvals_status"), "mission_approvals", ["status"], unique=False)

    # 3. Create mission_recovery_events table
    op.create_table(
        "mission_recovery_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("mission_id", sa.Uuid(), nullable=False),
        sa.Column("step_id", sa.String(length=100), nullable=False),
        sa.Column("strategy_used", sa.String(length=50), nullable=False),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_type", sa.String(length=100), nullable=False),
        sa.Column("outcome_status", sa.String(length=30), nullable=False),
        sa.Column("details_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["mission_id"], ["missions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_mission_recovery_events_id"), "mission_recovery_events", ["id"], unique=False)
    op.create_index(op.f("ix_mission_recovery_events_mission_id"), "mission_recovery_events", ["mission_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_mission_recovery_events_mission_id"), table_name="mission_recovery_events")
    op.drop_index(op.f("ix_mission_recovery_events_id"), table_name="mission_recovery_events")
    op.drop_table("mission_recovery_events")

    op.drop_index(op.f("ix_mission_approvals_status"), table_name="mission_approvals")
    op.drop_index(op.f("ix_mission_approvals_step_id"), table_name="mission_approvals")
    op.drop_index(op.f("ix_mission_approvals_mission_id"), table_name="mission_approvals")
    op.drop_index(op.f("ix_mission_approvals_id"), table_name="mission_approvals")
    op.drop_table("mission_approvals")

    op.drop_index(op.f("ix_mission_checkpoints_status"), table_name="mission_checkpoints")
    op.drop_index(op.f("ix_mission_checkpoints_checkpoint_id"), table_name="mission_checkpoints")
    op.drop_index(op.f("ix_mission_checkpoints_execution_id"), table_name="mission_checkpoints")
    op.drop_index(op.f("ix_mission_checkpoints_mission_id"), table_name="mission_checkpoints")
    op.drop_index(op.f("ix_mission_checkpoints_id"), table_name="mission_checkpoints")
    op.drop_table("mission_checkpoints")
