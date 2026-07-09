"""SQLAlchemy model definition for Session entities.

Maps active user session identifiers, cookies/bearer tokens index keys,
and expiration datetimes.
"""

from datetime import datetime
import uuid
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import BaseEntity


class Session(BaseEntity):
    """Session entity tracking user sessions validation tokens."""

    __tablename__ = "sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="sessions")
