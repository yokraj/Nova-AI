"""Configuration options for the Intelligent AI Model Router.
"""

from typing import Optional
from pydantic import BaseModel, Field

class RouterConfiguration(BaseModel):
    """Configuration options for routing behaviors, latency, and fallbacks."""

    default_model: str = Field("qwen2.5-coder", description="The default fallback model identifier.")
    max_latency_ms: int = Field(5000, description="Upper bound latency target.")
    enable_local_first: bool = Field(True, description="Prioritize local models execution.")
    enable_cloud_fallback: bool = Field(False, description="Allow automatic cloud model fallback when local fails.")
    max_memory_usage_mb: int = Field(8192, description="Upper RAM bounds limit.")
    fallback_attempts: int = Field(3, description="Maximum number of fallback retries.")
