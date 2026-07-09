"""SQLAlchemy model definition for UserPreference entities.

Maps user preference key-value pairs settings configurations profiles.
"""

import uuid
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import BaseEntity


class UserPreference(BaseEntity):
    """UserPreference entity tracking structured UI or logic settings mappings."""

    __tablename__ = "user_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationships
    user = relationship("User", back_populates="preferences")
