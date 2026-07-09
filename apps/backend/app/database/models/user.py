"""SQLAlchemy model definition for User entities.

Maps credentials, display names, statuses, roles, and cascade relationships.
"""

from typing import List, Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import BaseEntity
from app.database.models.enums import UserStatus


class User(BaseEntity):
    """User entity representing platform accounts credentials and profile configurations."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )
    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default=UserStatus.ACTIVE.value, nullable=False
    )
    role: Mapped[str] = mapped_column(
        String(20), default="user", nullable=False
    )

    # Relationships (One-to-Many cascade delete)
    conversations = relationship(
        "Conversation", back_populates="user", cascade="all, delete-orphan"
    )
    sessions = relationship(
        "Session", back_populates="user", cascade="all, delete-orphan"
    )
    refresh_tokens = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )
    preferences = relationship(
        "UserPreference", back_populates="user", cascade="all, delete-orphan"
    )
    provider_configs = relationship(
        "AIProviderConfiguration",
        back_populates="user",
        cascade="all, delete-orphan",
    )
