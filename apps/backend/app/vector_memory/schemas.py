"""Vector Memory Schemas Module.

Defines Pydantic DTO request/response schemas for embedding generation, batching,
vector search, similarity candidates, health diagnostics, and statistics.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class EmbeddingCreateRequest(BaseModel):
    """Request schema for generating single text embedding."""

    text: str = Field(min_length=1, description="Source text to embed")
    memory_id: Optional[str] = Field(default=None, description="Associated memory entry ID")
    model_name: Optional[str] = Field(default="BAAI/bge-small-en-v1.5", description="Embedding model tag")
    workspace: str = Field(default="Nova", description="Target workspace partition")
    project: Optional[str] = Field(default=None, description="Optional project association")


class BatchEmbeddingRequest(BaseModel):
    """Request schema for batch embedding generation."""

    texts: List[str] = Field(min_length=1, description="List of source texts")
    memory_ids: Optional[List[str]] = Field(default=None, description="Optional matching memory IDs")
    model_name: Optional[str] = Field(default="BAAI/bge-small-en-v1.5")
    workspace: str = Field(default="Nova")
    project: Optional[str] = Field(default=None)


class EmbeddingResponse(BaseModel):
    """Response DTO for generated embedding record."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    memory_id: str
    model_name: str
    dimension: int
    vector: List[float]
    workspace: str
    project: Optional[str] = None
    created_at: datetime


class VectorSearchRequest(BaseModel):
    """Request schema for vector similarity search."""

    query: str = Field(min_length=1, description="Search query text")
    top_k: int = Field(default=10, ge=1, le=100, description="Top-K candidate limit")
    workspace: Optional[str] = Field(default=None, description="Filter by workspace")
    project: Optional[str] = Field(default=None, description="Filter by project")
    metric: str = Field(default="cosine", description="Distance metric (cosine, euclidean, dot)")
    threshold: float = Field(default=0.0, ge=0.0, le=1.0, description="Minimum similarity score threshold")


class VectorSearchResult(BaseModel):
    """Response candidate item from vector similarity search."""

    memory_id: str
    similarity_score: float
    distance: float
    model_name: str
    workspace: str
    project: Optional[str] = None
    text_snippet: Optional[str] = None


class VectorHealthResponse(BaseModel):
    """Health diagnostic report for vector engine."""

    status: str = "healthy"
    index_valid: bool = True
    dimension_valid: bool = True
    cache_healthy: bool = True
    storage_healthy: bool = True
    model_healthy: bool = True
    details: Dict[str, Any] = Field(default_factory=dict)


class VectorStatisticsResponse(BaseModel):
    """Telemetry metrics summary for vector database."""

    model_config = ConfigDict(from_attributes=True)

    embedding_count: int
    vector_dimension: int
    average_search_latency: float
    average_embedding_latency: float
    cache_hits: int
    cache_misses: int
    index_size: int
    storage_usage: int
    timestamp: datetime
