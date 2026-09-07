"""SQLAlchemy model definition for Memory entities.
"""

import uuid
from sqlalchemy import String, Text, JSON, DateTime, ARRAY, Float
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone

from app.database.models.base import BaseEntity

# Attempt to import pgvector or fallback to standard array definition
try:
    from pgvector.sqlalchemy import Vector
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False

class MemoryModel(BaseEntity):
    """SQLAlchemy model tracking indexed memory segments and vector representations."""

    __tablename__ = "memories"

    content: Mapped[str] = mapped_column(Text, nullable=False)
    memory_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    importance_score: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)

    if HAS_PGVECTOR:
        embedding: Mapped[list] = mapped_column(Vector(768), nullable=True)
    else:
        embedding: Mapped[list] = mapped_column(JSON, nullable=True)
