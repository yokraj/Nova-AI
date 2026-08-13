"""Inference Gateway Database Models Module.

Defines SQLAlchemy ORM models for inference requests, registered model catalog,
token usage logs, and performance statistics.
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
)

from app.database.base import Base


def generate_uuid_str() -> str:
    """Generates string representation of UUID4."""
    return str(uuid.uuid4())


def current_utc_time() -> datetime:
    """Returns current UTC timestamp."""
    return datetime.now(timezone.utc)


class InferenceRequestModel(Base):
    """Inference execution request log table."""

    __tablename__ = "inference_requests"

    id = Column(String(36), primary_key=True, default=generate_uuid_str)
    prompt = Column(Text, nullable=False)
    model_name = Column(String(100), nullable=False, index=True)
    provider = Column(String(50), nullable=False, index=True)
    task_category = Column(String(50), nullable=False, default="General Chat")
    prompt_tokens = Column(Integer, nullable=False, default=0)
    completion_tokens = Column(Integer, nullable=False, default=0)
    total_tokens = Column(Integer, nullable=False, default=0)
    latency_ms = Column(Float, nullable=False, default=0.0)
    status = Column(String(20), nullable=False, default="completed")
    created_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time)


class RegisteredModelRecord(Base):
    """Registered AI models catalog table."""

    __tablename__ = "registered_models"

    id = Column(String(36), primary_key=True, default=generate_uuid_str)
    model_name = Column(String(100), nullable=False, unique=True, index=True)
    provider = Column(String(50), nullable=False, index=True)
    context_window = Column(Integer, nullable=False, default=8192)
    supports_vision = Column(Boolean, nullable=False, default=False)
    supports_function_calling = Column(Boolean, nullable=False, default=True)
    supports_streaming = Column(Boolean, nullable=False, default=True)
    vram_required_mb = Column(Integer, nullable=False, default=4096)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time)


class TokenLogModel(Base):
    """Token usage tracking log table."""

    __tablename__ = "inference_token_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid_str)
    request_id = Column(String(36), nullable=False, index=True)
    provider = Column(String(50), nullable=False, index=True)
    model_name = Column(String(100), nullable=False)
    prompt_tokens = Column(Integer, nullable=False, default=0)
    completion_tokens = Column(Integer, nullable=False, default=0)
    estimated_cost_usd = Column(Float, nullable=False, default=0.0)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=current_utc_time)


class InferenceStatisticsModel(Base):
    """Inference Gateway telemetry statistics table."""

    __tablename__ = "inference_statistics"

    id = Column(String(36), primary_key=True, default=generate_uuid_str)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=current_utc_time, index=True)
    total_requests = Column(Integer, nullable=False, default=0)
    total_tokens_processed = Column(Integer, nullable=False, default=0)
    average_ttft_ms = Column(Float, nullable=False, default=0.0)
    average_tokens_per_second = Column(Float, nullable=False, default=0.0)
    active_gpu_count = Column(Integer, nullable=False, default=0)
