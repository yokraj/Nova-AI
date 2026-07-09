"""SQLAlchemy model definition for Conversation entities.

Maps chat session identifiers, metadata header title descriptions, and statuses.
"""

import uuid
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import BaseEntity
from app.database.models.enums import ConversationStatus


class Conversation(BaseEntity):
    """Conversation entity tracking a chat thread associated with a User."""

    __tablename__ = "conversations"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=ConversationStatus.ACTIVE.value, nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )
