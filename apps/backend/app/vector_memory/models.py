"""Vector Memory Database Models Module.

Defines SQLAlchemy ORM models for embeddings, embedding models registry,
embedding jobs, vector indexes, and vector statistics.
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


class EmbeddingModel(Base):
    """Primary vector embedding record table."""

    __tablename__ = "embeddings"

    id = Column(String(36), primary_key=True, default=generate_uuid_str)
    memory_id = Column(String(36), nullable=False, index=True)
    model_name = Column(String(100), nullable=False, index=True, default="BAAI/bge-small-en-v1.5")
    dimension = Column(Integer, nullable=False, default=384)
    vector_json = Column(JSON, nullable=False)  # Serialized list of floats
    text_hash = Column(String(64), nullable=True, index=True)
    workspace = Column(String(100), nullable=False, default="Nova", index=True)
    project = Column(String(100), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time, onupdate=current_utc_time)


class EmbeddingModelRegistry(Base):
    """Registered embedding model metadata."""

    __tablename__ = "embedding_models"

    id = Column(String(36), primary_key=True, default=generate_uuid_str)
    model_name = Column(String(100), nullable=False, unique=True, index=True)
    provider = Column(String(50), nullable=False, default="sentence-transformers")
    dimension = Column(Integer, nullable=False, default=384)
    description = Column(Text, nullable=True)
    is_local = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time)


class EmbeddingJobModel(Base):
    """Asynchronous background embedding batch job tracker."""

    __tablename__ = "embedding_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid_str)
    job_type = Column(String(50), nullable=False, default="reindex")
    status = Column(String(30), nullable=False, default="pending", index=True)
    total_items = Column(Integer, nullable=False, default=0)
    processed_items = Column(Integer, nullable=False, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time)
    completed_at = Column(DateTime(timezone=True), nullable=True)


class VectorIndexModel(Base):
    """Vector index metadata and partition definitions."""

    __tablename__ = "vector_indexes"

    id = Column(String(36), primary_key=True, default=generate_uuid_str)
    index_name = Column(String(100), nullable=False, unique=True, index=True)
    backend = Column(String(50), nullable=False, default="sqlite")
    dimension = Column(Integer, nullable=False, default=384)
    vector_count = Column(Integer, nullable=False, default=0)
    metric = Column(String(20), nullable=False, default="cosine")
    created_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time, onupdate=current_utc_time)


class VectorStatisticsModel(Base):
    """Telemetry and performance metrics for vector database operations."""

    __tablename__ = "vector_statistics"

    id = Column(String(36), primary_key=True, default=generate_uuid_str)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=current_utc_time, index=True)
    embedding_count = Column(Integer, nullable=False, default=0)
    vector_dimension = Column(Integer, nullable=False, default=384)
    average_search_latency = Column(Float, nullable=False, default=0.0)
    average_embedding_latency = Column(Float, nullable=False, default=0.0)
    cache_hits = Column(Integer, nullable=False, default=0)
    cache_misses = Column(Integer, nullable=False, default=0)
    index_size = Column(Integer, nullable=False, default=0)
    storage_usage = Column(Integer, nullable=False, default=0)
