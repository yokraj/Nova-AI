"""Context Engine Schemas Module.

Defines Pydantic DTO request/response schemas for context building, optimization,
compression, quality evaluation, health diagnostics, and telemetry statistics.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class ContextBuildRequest(BaseModel):
    """Request schema for assembling LLM context."""

    query: str = Field(min_length=1, description="User query or prompt request")
    workspace: str = Field(default="Nova", description="Target workspace partition")
    project: Optional[str] = Field(default=None, description="Optional active project filter")
    token_budget: Optional[int] = Field(default=8192, description="Target LLM token budget (4K to 128K)")
    conversation_history: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    user_preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ContextBuildResponse(BaseModel):
    """Response DTO for built context package."""

    build_id: str
    query: str
    workspace: str
    project: Optional[str] = None
    context_text: str
    token_count: int
    token_budget: int
    compression_ratio: float
    quality_score: float
    sources_count: int
    created_at: datetime


class ContextOptimizeRequest(BaseModel):
    """Request schema for optimizing context content."""

    raw_context: str = Field(min_length=1)
    token_budget: int = Field(default=8192)


class ContextCompressRequest(BaseModel):
    """Request schema for compressing context text."""

    text: str = Field(min_length=1)
    target_ratio: float = Field(default=0.60, ge=0.1, le=1.0)


class QualityScoreReport(BaseModel):
    """Quality evaluation metrics report."""

    completeness: float
    coverage: float
    confidence: float
    freshness: float
    diversity: float
    overall_score: float


class ContextHealthResponse(BaseModel):
    """Health diagnostic report for context engine."""

    status: str = "healthy"
    builder_healthy: bool = True
    compression_healthy: bool = True
    cache_healthy: bool = True
    ranking_healthy: bool = True
    resolver_healthy: bool = True
    budget_engine_healthy: bool = True
    details: Dict[str, Any] = Field(default_factory=dict)


class ContextStatisticsResponse(BaseModel):
    """Telemetry metrics summary for context engine."""

    model_config = ConfigDict(from_attributes=True)

    total_assemblies: int
    average_context_size: int
    average_compression_ratio: float
    average_token_usage: int
    average_latency_ms: float
    cache_hit_rate: float
    average_quality_score: float
    timestamp: datetime
