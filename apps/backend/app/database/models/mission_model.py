"""SQLAlchemy models for Mission entities and Task breakdown.
"""

import uuid
from sqlalchemy import String, Text, Float, Integer, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import BaseEntity


class MissionModel(BaseEntity):
    """Mission entity tracking autonomous goal execution tasks."""

    __tablename__ = "missions"

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    goal: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="automation", index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PENDING", index=True)
    progress_percent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    assigned_agent: Mapped[str | None] = mapped_column(String(100), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    tasks = relationship(
        "MissionTaskModel", back_populates="mission", cascade="all, delete-orphan"
    )


class MissionTaskModel(BaseEntity):
    """Task breakdown item inside a Mission."""

    __tablename__ = "mission_tasks"

    mission_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("missions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    task_order: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PENDING", index=True)
    assigned_agent: Mapped[str | None] = mapped_column(String(100), nullable=True)
    dependencies_json: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)
    output_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    mission = relationship("MissionModel", back_populates="tasks")
