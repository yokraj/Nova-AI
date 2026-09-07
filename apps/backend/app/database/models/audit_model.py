"""SQLAlchemy model for Audit Event logging.
"""

from sqlalchemy import String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database.models.base import BaseEntity


class AuditEventModel(BaseEntity):
    """Audit log entry capturing security events, tool calls, and system actions."""

    __tablename__ = "audit_events"

    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    tool_name: Mapped[str | None] = mapped_column(String(150), nullable=True, index=True)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False, default="SAFE", index=True)
    actor: Mapped[str] = mapped_column(String(100), nullable=False, default="User")
    decision: Mapped[str] = mapped_column(String(30), nullable=False, default="ALLOWED")
    details_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
