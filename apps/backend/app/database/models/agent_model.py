"""SQLAlchemy models for Agent Workforce entities and Execution records.
"""

import uuid
from sqlalchemy import String, Text, Float, Integer, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import BaseEntity


class AgentModel(BaseEntity):
    """Agent entity tracking worker roles and capabilities."""

    __tablename__ = "agents"

    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="IDLE", index=True)
    capabilities_json: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)
    performance_score: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    tasks_completed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    executions = relationship(
        "AgentExecutionModel", back_populates="agent", cascade="all, delete-orphan"
    )


class AgentExecutionModel(BaseEntity):
    """Historical execution trace for an Agent."""

    __tablename__ = "agent_executions"

    agent_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    goal_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="COMPLETED")
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    logs_json: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)

    agent = relationship("AgentModel", back_populates="executions")
