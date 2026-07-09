"""SQLAlchemy model definition for AIProviderConfiguration entities.

Maps custom credentials, custom endpoint URLs bases, and default models configs.
"""

from typing import Optional
import uuid
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import BaseEntity


class AIProviderConfiguration(BaseEntity):
    """AIProviderConfiguration entity tracking user-configured AI credentials."""

    __tablename__ = "ai_provider_configurations"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider_name: Mapped[str] = mapped_column(String(100), nullable=False)
    api_key: Mapped[str] = mapped_column(String(255), nullable=False)
    api_base: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    model_defaults: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )

    # Relationships
    user = relationship("User", back_populates="provider_configs")
