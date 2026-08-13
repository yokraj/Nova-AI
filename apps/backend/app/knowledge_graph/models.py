"""Knowledge Graph Database Models Module.

Defines SQLAlchemy ORM models for graph entities, relationships, types registry,
path traces, and telemetry statistics.
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


class GraphEntityModel(Base):
    """Primary graph entity node table."""

    __tablename__ = "graph_entities"

    id = Column(String(36), primary_key=True, default=generate_uuid_str)
    name = Column(String(150), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)  # User, Project, Memory, CodeFile, etc.
    description = Column(Text, nullable=True)
    attributes = Column(JSON, nullable=True)  # Key-value metadata dictionary
    aliases = Column(JSON, nullable=True)     # Alias string list
    workspace = Column(String(100), nullable=False, default="Nova", index=True)
    project = Column(String(100), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time, onupdate=current_utc_time)


class GraphRelationshipModel(Base):
    """Primary graph relationship edge table."""

    __tablename__ = "graph_relationships"

    id = Column(String(36), primary_key=True, default=generate_uuid_str)
    source_id = Column(String(36), ForeignKey("graph_entities.id", ondelete="CASCADE"), nullable=False, index=True)
    target_id = Column(String(36), ForeignKey("graph_entities.id", ondelete="CASCADE"), nullable=False, index=True)
    relationship_type = Column(String(50), nullable=False, index=True)  # depends_on, implements, uses, calls, etc.
    weight = Column(Float, nullable=False, default=1.0)
    attributes = Column(JSON, nullable=True)
    workspace = Column(String(100), nullable=False, default="Nova", index=True)
    project = Column(String(100), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time)


class GraphTypeModel(Base):
    """Registry of entity and relationship types."""

    __tablename__ = "graph_types"

    id = Column(String(36), primary_key=True, default=generate_uuid_str)
    type_category = Column(String(20), nullable=False)  # "entity" or "relationship"
    type_name = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time)


class GraphPathModel(Base):
    """Cached graph paths and multi-hop traversal traces."""

    __tablename__ = "graph_paths"

    id = Column(String(36), primary_key=True, default=generate_uuid_str)
    start_entity_id = Column(String(36), nullable=False, index=True)
    end_entity_id = Column(String(36), nullable=False, index=True)
    path_nodes = Column(JSON, nullable=False)        # List of node IDs
    path_edges = Column(JSON, nullable=False)        # List of relationship IDs
    hop_count = Column(Integer, nullable=False, default=1)
    total_weight = Column(Float, nullable=False, default=1.0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time)


class GraphStatisticsModel(Base):
    """Telemetry and graph topological metrics table."""

    __tablename__ = "graph_statistics"

    id = Column(String(36), primary_key=True, default=generate_uuid_str)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=current_utc_time, index=True)
    entity_count = Column(Integer, nullable=False, default=0)
    relationship_count = Column(Integer, nullable=False, default=0)
    graph_density = Column(Float, nullable=False, default=0.0)
    connected_components = Column(Integer, nullable=False, default=1)
    average_degree = Column(Float, nullable=False, default=0.0)
    query_latency = Column(Float, nullable=False, default=0.0)
    traversal_latency = Column(Float, nullable=False, default=0.0)
    storage_usage = Column(Integer, nullable=False, default=0)
