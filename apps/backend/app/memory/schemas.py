"""Memory Schemas Module.

Defines Pydantic DTO request and response models for memory management,
searching, relationships, workspace/project isolation, user preferences, and statistics.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

from app.memory.memory_types import MemoryType, RelationshipType


class MemoryEntryCreate(BaseModel):
    """Schema for creating a new memory entry."""

    title: str = Field(min_length=1, max_length=255, description="Memory title")
    content: str = Field(min_length=1, description="Full text content of memory")
    summary: Optional[str] = Field(default=None, description="Optional brief summary")
    memory_type: MemoryType = Field(default=MemoryType.LONG_TERM, description="Classification category")
    workspace: str = Field(default="Nova", description="Target workspace partition")
    project: Optional[str] = Field(default=None, description="Optional project association")
    user_id: str = Field(default="system_user", description="Owner user identifier")
    importance: float = Field(default=0.5, ge=0.0, le=1.0, description="Importance weight score")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Factual confidence score")
    is_pinned: bool = Field(default=False, description="Pin status flag")
    expires_at: Optional[datetime] = Field(default=None, description="Optional expiration timestamp")
    tags: List[str] = Field(default_factory=list, description="Associated tag labels")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Custom metadata dictionary")


class MemoryEntryUpdate(BaseModel):
    """Schema for updating an existing memory entry."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    content: Optional[str] = Field(default=None, min_length=1)
    summary: Optional[str] = Field(default=None)
    memory_type: Optional[MemoryType] = Field(default=None)
    importance: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    is_pinned: Optional[bool] = Field(default=None)
    is_archived: Optional[bool] = Field(default=None)
    expires_at: Optional[datetime] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)
    metadata: Optional[Dict[str, Any]] = Field(default=None)


class MemoryRelationshipCreate(BaseModel):
    """Schema for creating inter-memory relationship link."""

    source_id: str = Field(description="Source memory ID")
    target_id: str = Field(description="Target memory ID")
    relationship_type: RelationshipType = Field(description="Type of relationship linkage")
    weight: float = Field(default=1.0, ge=0.0, le=5.0, description="Relationship strength weight")


class MemoryEntryResponse(BaseModel):
    """Response DTO for memory entry."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    content: str
    summary: Optional[str] = None
    memory_type: MemoryType
    workspace: str
    project: Optional[str] = None
    user_id: str
    importance: float
    confidence: float
    access_count: int
    is_pinned: bool
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    calculated_score: Optional[float] = None


class MemorySearchQuery(BaseModel):
    """Search query parameter options."""

    query: str = Field(default="", description="Search query string")
    workspace: Optional[str] = Field(default=None, description="Filter by workspace")
    project: Optional[str] = Field(default=None, description="Filter by project")
    user_id: Optional[str] = Field(default=None, description="Filter by user")
    memory_type: Optional[MemoryType] = Field(default=None, description="Filter by memory type")
    tags: List[str] = Field(default_factory=list, description="Filter by tag list")
    min_importance: float = Field(default=0.0, ge=0.0, le=1.0)
    limit: int = Field(default=20, ge=1, le=100)


class WorkspaceMemorySchema(BaseModel):
    """Workspace memory representation schema."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_name: str
    description: Optional[str] = None
    active_projects_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class ProjectMemorySchema(BaseModel):
    """Project memory representation schema."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    project_name: str
    workspace_name: str
    architecture_summary: Optional[str] = None
    requirements_summary: Optional[str] = None
    decisions_summary: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class UserPreferenceSchema(BaseModel):
    """User preferences schema."""

    user_id: str
    writing_style: Optional[str] = None
    favorite_languages: List[str] = Field(default_factory=list)
    favorite_frameworks: List[str] = Field(default_factory=list)
    frequent_tools: List[str] = Field(default_factory=list)
    coding_style: Optional[str] = None
    preferences_json: Dict[str, Any] = Field(default_factory=dict)


class MemoryStatisticsSchema(BaseModel):
    """Memory statistics telemetry summary."""

    memory_count: int
    workspace_count: int
    project_count: int
    compression_ratio: float
    retrieval_count: int
    search_latency_ms: float
    storage_usage_bytes: int
    timestamp: datetime
