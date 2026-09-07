"""SQLAlchemy models for Skill entities and Version history.
"""

from datetime import datetime, timezone
import uuid
from sqlalchemy import String, Text, Float, Integer, JSON, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import BaseEntity


class SkillModel(BaseEntity):
    """Primary skill table storing learned multi-step workflow capabilities."""

    __tablename__ = "skills"

    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="general", index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active", index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.9)
    success_rate: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    owner: Mapped[str] = mapped_column(String(100), nullable=False, default="NovaUser")
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="user_taught")

    trigger_patterns_json: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)
    required_tools_json: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)
    variables_json: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)
    steps_json: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    versions = relationship(
        "SkillVersionModel", back_populates="skill", cascade="all, delete-orphan"
    )


class SkillVersionModel(BaseEntity):
    """Skill version revision history table."""

    __tablename__ = "skill_versions"

    skill_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    changes: Mapped[str] = mapped_column(Text, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    steps_snapshot_json: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)
    success_rate_snapshot: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    skill = relationship("SkillModel", back_populates="versions")
