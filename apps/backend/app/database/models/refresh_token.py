"""SQLAlchemy model definition for RefreshToken entities.

Tracks active user logins, rotations, revokes state, and lifecycle expirations.
"""

from datetime import datetime
import uuid
from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import BaseEntity


class RefreshToken(BaseEntity):
    """RefreshToken tracking entity supporting token family rotation protections."""

    __tablename__ = "refresh_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    is_revoked: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="refresh_tokens")

    @property
    def revoked(self) -> bool:
        """Alias for is_revoked for service compatibility."""
        return self.is_revoked

    @revoked.setter
    def revoked(self, value: bool) -> None:
        self.is_revoked = value

