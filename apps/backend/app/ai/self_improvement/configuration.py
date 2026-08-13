"""Configuration settings and schemas for Autonomous Self-Improvement & Adaptive Intelligence Engine.
"""

from typing import Any, Dict
from pydantic import BaseModel, Field


class SelfImprovementConfiguration(BaseModel):
    """Configuration schema for Self-Improvement and Adaptive Intelligence platform."""

    auto_distill_workflows: bool = Field(True, description="Automatically distill repeated workflows into skills and templates")
    evaluation_interval_hours: int = Field(24, description="Interval in hours for scheduled self-evaluation benchmarking")
    min_confidence_threshold: float = Field(0.85, description="Minimum confidence threshold required to apply self-optimizations")
    safety_lock_enabled: bool = Field(True, description="Enforce strict safety boundary locks for behavior adaptation")
    max_history_reports: int = Field(100, description="Maximum historical benchmark and quality reports stored")
    cache_ttl_seconds: int = Field(3600, description="Cache TTL for benchmark and optimization recommendations")
    extra_settings: Dict[str, Any] = Field(default_factory=dict, description="Additional custom configuration settings")
