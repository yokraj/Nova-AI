"""SQLAlchemy models for Mission Checkpoints, Approvals, and Recovery Events.
"""

import uuid
from sqlalchemy import String, Text, Integer, Boolean, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import BaseEntity


class MissionCheckpointModel(BaseEntity):
    """Persistent execution snapshot for long-running mission recovery."""

    __tablename__ = "mission_checkpoints"

    mission_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("missions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    execution_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    checkpoint_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="EXECUTING", index=True)
    current_step: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completed_steps_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    pending_steps_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    retry_counters_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    budget_state_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    approval_state_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    verification_results_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    checkpoint_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_safe_resumable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    mission = relationship("MissionModel", backref="checkpoints")


class MissionApprovalModel(BaseEntity):
    """Persistent approval request for high-risk mission actions."""

    __tablename__ = "mission_approvals"

    mission_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("missions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    step_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(30), nullable=False, default="HIGH")
    target_details_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PENDING", index=True)
    authorized_by: Mapped[str | None] = mapped_column(String(100), nullable=True)

    mission = relationship("MissionModel", backref="approvals")


class MissionRecoveryEventModel(BaseEntity):
    """Audit log of recovery attempts and strategies used during mission execution."""

    __tablename__ = "mission_recovery_events"

    mission_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("missions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    step_id: Mapped[str] = mapped_column(String(100), nullable=False)
    strategy_used: Mapped[str] = mapped_column(String(50), nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_type: Mapped[str] = mapped_column(String(100), nullable=False)
    outcome_status: Mapped[str] = mapped_column(String(30), nullable=False)
    details_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    mission = relationship("MissionModel", backref="recovery_events")
