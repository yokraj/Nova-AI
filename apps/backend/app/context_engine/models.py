"""Context Engine Database Models Module.

Defines SQLAlchemy ORM models for context build records, context package cache,
quality evaluation logs, and telemetry statistics.
"""

from datetime import datetime, timezone
import uuid

from sqlalchemy import (
    Column,
    String,
    Text,
    Float,
    Integer,
    Boolean,
    DateTime,
    JSON,
    ForeignKey,
)

from app.database.base import Base


def generate_uuid_str() -> str:
    """Generates string representation of UUID4."""
    return str(uuid.uuid4())


def current_utc_time() -> datetime:
    """Returns current UTC timestamp."""
    return datetime.now(timezone.utc)


class ContextBuildModel(Base):
    """Primary context assembly build record table."""

    __tablename__ = "context_builds"

    id = Column(String(36), primary_key=True, default=generate_uuid_str)
    query = Column(Text, nullable=False)
    workspace = Column(String(100), nullable=False, default="Nova", index=True)
    project = Column(String(100), nullable=True, index=True)
    token_budget = Column(Integer, nullable=False, default=8192)
    final_token_count = Column(Integer, nullable=False, default=0)
    compression_ratio = Column(Float, nullable=False, default=1.0)
    quality_score = Column(Float, nullable=False, default=0.9)
    created_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time)


class ContextCacheModel(Base):
    """Context package LRU cache entry table."""

    __tablename__ = "context_cache"

    id = Column(String(36), primary_key=True, default=generate_uuid_str)
    query_hash = Column(String(64), nullable=False, unique=True, index=True)
    context_text = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time)
    expires_at = Column(DateTime(timezone=True), nullable=True)


class ContextQualityModel(Base):
    """Quality evaluation logs (completeness, coverage, confidence, freshness)."""

    __tablename__ = "context_quality_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid_str)
    build_id = Column(String(36), ForeignKey("context_builds.id", ondelete="CASCADE"), nullable=False, index=True)
    completeness = Column(Float, nullable=False, default=1.0)
    coverage = Column(Float, nullable=False, default=1.0)
    confidence = Column(Float, nullable=False, default=1.0)
    freshness = Column(Float, nullable=False, default=1.0)
    diversity = Column(Float, nullable=False, default=1.0)
    overall_score = Column(Float, nullable=False, default=1.0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time)


class ContextStatisticsModel(Base):
    """Telemetry metrics table for context engine operations."""

    __tablename__ = "context_statistics"

    id = Column(String(36), primary_key=True, default=generate_uuid_str)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=current_utc_time, index=True)
    total_assemblies = Column(Integer, nullable=False, default=0)
    average_context_size = Column(Integer, nullable=False, default=0)
    average_compression_ratio = Column(Float, nullable=False, default=1.0)
    average_token_usage = Column(Integer, nullable=False, default=0)
    average_latency_ms = Column(Float, nullable=False, default=0.0)
    cache_hit_rate = Column(Float, nullable=False, default=0.0)
    average_quality_score = Column(Float, nullable=False, default=0.0)
