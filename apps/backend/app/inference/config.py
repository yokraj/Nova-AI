"""Inference Gateway Configuration Module.

Defines Pydantic settings for default local providers (Ollama, llama.cpp, vLLM, LM Studio),
cloud provider credentials, GPU scheduling bounds, retry parameters, and circuit breakers.
"""

import os
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class InferenceConfig(BaseModel):
    """Configuration settings for Enterprise Inference Gateway."""

    # Default Local Provider & Model Selection (Enforced by Zero-Cost Policy)
    default_provider: str = Field(default="ollama", description="Default LLM provider (ollama only)")
    default_model: str = Field(
        default_factory=lambda: os.getenv("AI_DEFAULT_MODEL", "qwen3:8b"),
        description="Default LLM model name",
    )
    ollama_base_url: str = Field(
        default_factory=lambda: os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434"),
        description="Ollama API base URL",
    )
    vllm_base_url: str = Field(default="http://localhost:8000", description="vLLM API base URL (local only)")
    openai_compatible_base_url: str = Field(default="http://localhost:1234/v1", description="OpenAI-compatible local server URL (e.g. LM Studio / vLLM)")

    # Legacy Cloud Provider Fields (Disabled & Inactive under Zero-Cost Policy)
    openai_api_key: Optional[str] = Field(default=None, description="Disabled under Zero-Cost Policy")
    anthropic_api_key: Optional[str] = Field(default=None, description="Disabled under Zero-Cost Policy")
    gemini_api_key: Optional[str] = Field(default=None, description="Disabled under Zero-Cost Policy")

    # GPU & Execution Settings
    max_gpu_allocation: int = Field(default=4, description="Maximum available GPUs for scheduling")
    max_vram_reservation_mb: int = Field(default=24576, description="Max VRAM allocation per GPU (24GB)")
    max_concurrent_requests: int = Field(default=1000, description="Max concurrent request limit")
    gateway_timeout_seconds: float = Field(default=120.0, description="Request gateway timeout threshold")

    # Circuit Breaker & Retry Settings
    max_retries: int = Field(default=3, description="Max retry attempts on failure")
    circuit_breaker_failure_threshold: int = Field(default=5, description="Consecutive failures to open circuit breaker")
    circuit_breaker_recovery_seconds: float = Field(default=30.0, description="Cooldown time before attempting half-open state")
