"""Context Engine Configuration Module.

Defines Pydantic settings for adaptive token budgets (4K to 128K context windows),
compression targets, fusion weights, and quality score bounds.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ContextEngineConfig(BaseModel):
    """Configuration settings for Enterprise Context Engine."""

    # Token Budget Window Bounds
    default_token_budget: int = Field(default=8192, description="Default LLM token budget window")
    max_token_budget: int = Field(default=131072, description="Maximum supported context window (128K)")
    supported_context_windows: List[int] = Field(
        default_factory=lambda: [4096, 8192, 16384, 32768, 65536, 131072]
    )

    # Fusion & Ranking Weights
    weight_semantic: float = Field(default=0.35, description="Weight for semantic vector similarity")
    weight_confidence: float = Field(default=0.20, description="Weight for source confidence score")
    weight_recency: float = Field(default=0.15, description="Weight for recency temporal decay")
    weight_project: float = Field(default=0.15, description="Weight for project relevance")
    weight_workspace: float = Field(default=0.15, description="Weight for workspace relevance")

    # Compression & Cache Settings
    compression_target_ratio: float = Field(default=0.60, description="Target compression ratio (60% size reduction)")
    cache_capacity: int = Field(default=2000, description="Max capacity for context package cache")
    min_quality_score_threshold: float = Field(default=0.70, description="Quality score threshold for validation")
