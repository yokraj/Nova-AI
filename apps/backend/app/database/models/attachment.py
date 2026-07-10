"""SQLAlchemy model definition for Attachment entities.

Maps uploaded file metadata attachments associated with messages.
"""

import uuid
from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import BaseEntity


class Attachment(BaseEntity):
    """Attachment entity representing files uploaded within chat messages."""

    __tablename__ = "attachments"

    message_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # AttachmentType
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    message = relationship("Message", back_populates="attachments")
