"""Configuration settings and schemas for Nova Universal Knowledge, Research & Reasoning Engine.
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class ResearchConfiguration(BaseModel):
    """Configuration schema for Universal Knowledge, Research & Reasoning Engine."""

    max_sub_questions: int = Field(5, description="Maximum sub-questions generated per research query")
    confidence_threshold: float = Field(0.70, description="Minimum confidence score required for claim verification")
    duplicate_similarity_threshold: float = Field(0.85, description="Text similarity threshold for duplicate source detection")
    default_citation_style: str = Field("APA", description="Default citation format (APA, BibTeX, Markdown)")
    knowledge_graph_path: str = Field("./data/knowledge_graph.json", description="Local Knowledge Graph storage path")
    enable_voice_summaries: bool = Field(True, description="Enables spoken voice summaries for research completion")
    cache_ttl_seconds: int = Field(7200, description="Cache expiration duration for research queries")
    telemetry_enabled: bool = Field(True, description="Collect research metrics and verification traces")
    extra_settings: Dict[str, Any] = Field(default_factory=dict, description="Additional custom settings")
