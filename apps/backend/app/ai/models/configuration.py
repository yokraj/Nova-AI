"""Configuration settings and schemas for Nova Multi-Model AI Integration Platform.
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class ModelPlatformConfiguration(BaseModel):
    """Configuration schema for Multi-Model AI Integration Platform & Router."""

    max_vram_gb: float = Field(8.0, description="Maximum GPU VRAM allocated for local model loading")
    default_provider_preference: str = Field("ollama", description="Preferred local model provider backend (ollama, llamacpp, transformers)")
    fallback_enabled: bool = Field(True, description="Automatically fallback to alternative provider or mock if target fails")
    load_balancing_enabled: bool = Field(True, description="Distribute requests across multiple active instances")
    cache_ttl_seconds: int = Field(3600, description="Cache duration for generation & embedding outputs")
    telemetry_enabled: bool = Field(True, description="Collect model routing and inference metrics")
    ollama_base_url: str = Field("http://localhost:11434", description="Local Ollama REST service endpoint")
    model_download_dir: str = Field("./data/models", description="Local model checkpoint download directory")
    extra_settings: Dict[str, Any] = Field(default_factory=dict, description="Additional custom settings")
