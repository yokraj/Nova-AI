"""Memory Database Models Module.

Defines SQLAlchemy ORM models for memory entries, chunks, tags, relationships,
workspace memories, project memories, conversation memories, user preferences, and statistics.
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
    Index,
)
from sqlalchemy.orm import relationship

from app.database.base import Base


def generate_uuid_str() -> str:
    """Generates string representation of UUID4."""
    return str(uuid.uuid4())


def current_utc_time() -> datetime:
    """Returns current UTC timestamp."""
    return datetime.now(timezone.utc)


class MemoryEntryModel(Base):
    """Primary memory entry model representing long-term/short-term/workspace memories."""

    __tablename__ = "memory_entries"

    id = Column(String(36), primary_key=True, default=generate_uuid_str)
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    memory_type = Column(String(50), nullable=False, index=True, default="long_term")
    workspace = Column(String(100), nullable=False, default="Nova", index=True)
    project = Column(String(100), nullable=True, index=True)
    user_id = Column(String(100), nullable=False, default="system_user", index=True)
    
    importance = Column(Float, nullable=False, default=0.5)
    confidence = Column(Float, nullable=False, default=1.0)
    access_count = Column(Integer, nullable=False, default=0)
    is_pinned = Column(Boolean, nullable=False, default=False)
    is_archived = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time, onupdate=current_utc_time)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    metadata_json = Column(JSON, nullable=True)

    # Relationships
    chunks = relationship("MemoryChunkModel", back_populates="memory_entry", cascade="all, delete-orphan")
    tags = relationship("MemoryTagModel", back_populates="memory_entry", cascade="all, delete-orphan")
    source_relationships = relationship("MemoryRelationshipModel", foreign_keys="MemoryRelationshipModel.source_id", back_populates="source_memory", cascade="all, delete-orphan")
    target_relationships = relationship("MemoryRelationshipModel", foreign_keys="MemoryRelationshipModel.target_id", back_populates="target_memory", cascade="all, delete-orphan")


class MemoryChunkModel(Base):
    """Decomposed chunks of large memory entries for granular retrieval."""

    __tablename__ = "memory_chunks"

    id = Column(String(36), primary_key=True, default=generate_uuid_str)
    memory_id = Column(String(36), ForeignKey("memory_entries.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    chunk_summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time)

    memory_entry = relationship("MemoryEntryModel", back_populates="chunks")


class MemoryTagModel(Base):
    """Tags associated with memory entries."""

    __tablename__ = "memory_tags"

    id = Column(String(36), primary_key=True, default=generate_uuid_str)
    memory_id = Column(String(36), ForeignKey("memory_entries.id", ondelete="CASCADE"), nullable=False, index=True)
    tag_name = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time)

    memory_entry = relationship("MemoryEntryModel", back_populates="tags")


class MemoryRelationshipModel(Base):
    """Inter-memory linkages (references, depends_on, related_to, supersedes, etc.)."""

    __tablename__ = "memory_relationships"

    id = Column(String(36), primary_key=True, default=generate_uuid_str)
    source_id = Column(String(36), ForeignKey("memory_entries.id", ondelete="CASCADE"), nullable=False, index=True)
    target_id = Column(String(36), ForeignKey("memory_entries.id", ondelete="CASCADE"), nullable=False, index=True)
    relationship_type = Column(String(50), nullable=False, index=True)
    weight = Column(Float, nullable=False, default=1.0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time)

    source_memory = relationship("MemoryEntryModel", foreign_keys=[source_id], back_populates="source_relationships")
    target_memory = relationship("MemoryEntryModel", foreign_keys=[target_id], back_populates="target_relationships")


class WorkspaceMemoryModel(Base):
    """Workspace-level settings, rules, and workspace memory mapping."""

    __tablename__ = "workspace_memories"

    id = Column(String(36), primary_key=True, default=generate_uuid_str)
    workspace_name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    active_projects_count = Column(Integer, nullable=False, default=0)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time, onupdate=current_utc_time)


class ProjectMemoryModel(Base):
    """Project-level architectural decisions, requirements, tasks, and history."""

    __tablename__ = "project_memories"

    id = Column(String(36), primary_key=True, default=generate_uuid_str)
    project_name = Column(String(100), nullable=False, index=True)
    workspace_name = Column(String(100), nullable=False, index=True)
    architecture_summary = Column(Text, nullable=True)
    requirements_summary = Column(Text, nullable=True)
    decisions_summary = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time, onupdate=current_utc_time)


class ConversationMemoryModel(Base):
    """Conversation thread metadata and multi-turn dialog history."""

    __tablename__ = "conversation_memories"

    id = Column(String(36), primary_key=True, default=generate_uuid_str)
    conversation_id = Column(String(100), nullable=False, unique=True, index=True)
    title = Column(String(255), nullable=True)
    workspace_name = Column(String(100), nullable=False, default="Nova")
    project_name = Column(String(100), nullable=True)
    turn_count = Column(Integer, nullable=False, default=0)
    is_compressed = Column(Boolean, nullable=False, default=False)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time, onupdate=current_utc_time)


class UserPreferenceModel(Base):
    """User preference profiles, writing styles, and favorite tools."""

    __tablename__ = "user_preferences"

    id = Column(String(36), primary_key=True, default=generate_uuid_str)
    user_id = Column(String(100), nullable=False, unique=True, index=True)
    writing_style = Column(String(255), nullable=True)
    favorite_languages = Column(JSON, nullable=True)
    favorite_frameworks = Column(JSON, nullable=True)
    frequent_tools = Column(JSON, nullable=True)
    coding_style = Column(Text, nullable=True)
    preferences_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time, onupdate=current_utc_time)


class MemoryStatisticsModel(Base):
    """Aggregated memory platform telemetry and statistics."""

    __tablename__ = "memory_statistics"

    id = Column(String(36), primary_key=True, default=generate_uuid_str)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=current_utc_time, index=True)
    memory_count = Column(Integer, nullable=False, default=0)
    workspace_count = Column(Integer, nullable=False, default=0)
    project_count = Column(Integer, nullable=False, default=0)
    compression_ratio = Column(Float, nullable=False, default=1.0)
    retrieval_count = Column(Integer, nullable=False, default=0)
    search_latency_ms = Column(Float, nullable=False, default=0.0)
    storage_usage_bytes = Column(Integer, nullable=False, default=0)
