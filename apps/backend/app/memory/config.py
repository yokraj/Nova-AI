"""Memory Configuration Module.

Defines Pydantic settings for memory retention, scoring weights, compression limits, and cleanup schedules.
"""

from typing import Dict
from pydantic import BaseModel, Field


class MemoryConfig(BaseModel):
    """Configuration structure for Enterprise Memory & Knowledge Foundation."""

    # Default Retention & Scoping
    default_workspace: str = Field(default="Nova", description="Default workspace scoping name")
    default_user_id: str = Field(default="system_user", description="Default user identifier")
    max_memory_entries: int = Field(default=100000, description="Max total memory entry limit")
    
    # Retention Bounds (in days)
    short_term_ttl_days: float = Field(default=7.0, description="TTL for short-term memories in days")
    temporary_ttl_hours: float = Field(default=24.0, description="TTL for temporary memories in hours")

    # Memory Scoring Weights (sum to 1.0)
    weight_importance: float = Field(default=0.30, description="Weight for importance score")
    weight_recency: float = Field(default=0.25, description="Weight for recency score")
    weight_frequency: float = Field(default=0.20, description="Weight for usage frequency score")
    weight_relevance: float = Field(default=0.15, description="Weight for search relevance score")
    weight_confidence: float = Field(default=0.10, description="Weight for confidence score")

    # Compression & Cleanup
    compression_threshold_entries: int = Field(default=50, description="Trigger compression when thread entries hit count")
    cleanup_interval_seconds: float = Field(default=3600.0, description="Interval for automated background cleanup")
