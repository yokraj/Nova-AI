"""RAG Configuration Module.

Defines Pydantic settings for hybrid search weights, cross-encoder reranking parameters,
token budgets, context compression ratios, and grounding confidence thresholds.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class RAGConfig(BaseModel):
    """Configuration settings for Enterprise Hybrid RAG Engine."""

    # Search & Fusion Weights
    keyword_weight: float = Field(default=0.40, description="Weight for BM25/keyword retrieval score")
    semantic_weight: float = Field(default=0.60, description="Weight for vector semantic retrieval score")
    rrf_k: int = Field(default=60, description="Reciprocal Rank Fusion smoothing parameter")
    top_candidates_limit: int = Field(default=50, description="Max candidate pool size before reranking")
    rerank_top_k: int = Field(default=10, description="Top candidates retained post cross-encoder reranking")

    # Context & Token Budget Bounds
    max_context_tokens: int = Field(default=4096, description="Maximum token budget for LLM context assembly")
    max_chunk_tokens: int = Field(default=512, description="Target token budget per retrieved text chunk")

    # Grounding & Verification Thresholds
    min_grounding_confidence: float = Field(default=0.75, description="Threshold below which uncertainty is stated")
    strict_grounding_mode: bool = Field(default=True, description="Enforces zero fact invention and strict citations")
