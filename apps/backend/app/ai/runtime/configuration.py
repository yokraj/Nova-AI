"""Configuration settings and schemas for Real AI Runtime Integration & Local Model Execution Platform.
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class RuntimeConfiguration(BaseModel):
    """Configuration schema for AI Runtime Execution Platform."""

    max_vram_gb: float = Field(8.0, description="Maximum GPU VRAM allocation ceiling in GB")
    max_ram_gb: float = Field(16.0, description="Maximum System RAM allocation ceiling in GB")
    default_device: str = Field("cuda", description="Default preferred compute device ('cuda', 'cpu', 'directml')")
    cpu_fallback_enabled: bool = Field(True, description="Automatically fallback to CPU compute if GPU VRAM is full")
    models_directory: str = Field("./data/models", description="Directory path for downloaded model weights")
    cache_ttl_seconds: int = Field(3600, description="Cache expiration TTL for inference results")
    telemetry_enabled: bool = Field(True, description="Enable hardware resource monitoring and metrics collection")
    extra_settings: Dict[str, Any] = Field(default_factory=dict, description="Additional custom runtime settings")
