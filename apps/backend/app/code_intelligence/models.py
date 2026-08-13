"""Code Intelligence Database Models Module.

Defines SQLAlchemy ORM models for repositories, code symbols, code dependencies,
architectural components, and telemetry statistics.
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


class RepositoryModel(Base):
    """Primary indexed repository metadata table."""

    __tablename__ = "repositories"

    id = Column(String(36), primary_key=True, default=generate_uuid_str)
    name = Column(String(150), nullable=False, index=True)
    root_path = Column(Text, nullable=False)
    primary_language = Column(String(50), nullable=False, default="Python", index=True)
    frameworks = Column(JSON, nullable=True)     # List of frameworks detected
    file_count = Column(Integer, nullable=False, default=0)
    lines_of_code = Column(Integer, nullable=False, default=0)
    workspace = Column(String(100), nullable=False, default="Nova", index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time, onupdate=current_utc_time)


class CodeSymbolModel(Base):
    """Indexed source code symbol table (classes, functions, methods, routes, tables)."""

    __tablename__ = "code_symbols"

    id = Column(String(36), primary_key=True, default=generate_uuid_str)
    repository_id = Column(String(36), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(150), nullable=False, index=True)
    symbol_type = Column(String(50), nullable=False, index=True)  # Class, Function, Method, Route, Table
    file_path = Column(Text, nullable=False)
    start_line = Column(Integer, nullable=False, default=1)
    end_line = Column(Integer, nullable=False, default=1)
    signature = Column(Text, nullable=True)
    docstring = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time)


class CodeDependencyModel(Base):
    """Source code module and package dependency edge table."""

    __tablename__ = "code_dependencies"

    id = Column(String(36), primary_key=True, default=generate_uuid_str)
    repository_id = Column(String(36), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    source_symbol = Column(String(150), nullable=False, index=True)
    target_symbol = Column(String(150), nullable=False, index=True)
    dependency_type = Column(String(50), nullable=False, default="imports")  # imports, calls, inherits
    created_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time)


class ArchitectureComponentModel(Base):
    """Detected software architectural patterns and components."""

    __tablename__ = "architecture_components"

    id = Column(String(36), primary_key=True, default=generate_uuid_str)
    repository_id = Column(String(36), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    pattern_name = Column(String(100), nullable=False, index=True)  # MVC, Clean Architecture, Microservices
    component_name = Column(String(100), nullable=False)
    file_paths = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=current_utc_time)


class CodeStatisticsModel(Base):
    """Telemetry and performance metrics table for code intelligence."""

    __tablename__ = "code_statistics"

    id = Column(String(36), primary_key=True, default=generate_uuid_str)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=current_utc_time, index=True)
    repositories_indexed = Column(Integer, nullable=False, default=0)
    files_indexed = Column(Integer, nullable=False, default=0)
    classes_indexed = Column(Integer, nullable=False, default=0)
    functions_indexed = Column(Integer, nullable=False, default=0)
    apis_indexed = Column(Integer, nullable=False, default=0)
    tables_indexed = Column(Integer, nullable=False, default=0)
    relationships_discovered = Column(Integer, nullable=False, default=0)
    indexing_latency = Column(Float, nullable=False, default=0.0)
    storage_usage = Column(Integer, nullable=False, default=0)
