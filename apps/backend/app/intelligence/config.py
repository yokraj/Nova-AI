"""Intelligence Engine Configuration Module.

Defines Pydantic configuration settings for Nova AI Universal Intelligence Engine,
including model parameters, memory capacity, reasoning depth, and routing defaults.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ModelProviderConfig(BaseModel):
    """Configuration for an individual LLM provider or local runtime."""

    provider_id: str = Field(description="Unique provider identifier (e.g. ollama, llama.cpp, openai, anthropic)")
    base_url: str = Field(default="http://localhost:11434", description="Base URL endpoint")
    api_key: Optional[str] = Field(default=None, description="API authorization key if required")
    default_model: str = Field(default="llama3.2:latest", description="Default model tag or identifier")
    timeout_seconds: float = Field(default=60.0, description="Request timeout limit in seconds")
    is_local: bool = Field(default=True, description="True if local-first offline runtime")
    is_enabled: bool = Field(default=True, description="Whether the provider is permitted under Zero-Cost Policy")


class IntelligenceConfig(BaseModel):
    """Master configuration structure for Universal Intelligence Engine."""

    # Default Reasoning & Model Parameters
    default_provider: str = Field(default="ollama", description="Primary model provider")
    default_model: str = Field(default="llama3.2:latest", description="Primary LLM identifier")
    fast_model: str = Field(default="llama3.2:3b", description="Fast model for intent and light tasks")
    coding_model: str = Field(default="qwen2.5-coder:latest", description="Specialized code generation model")
    reasoning_model: str = Field(default="deepseek-r1:latest", description="Deep reasoning and logic model")
    temperature: float = Field(default=0.7, description="Generation temperature (0.0 to 1.0)")
    max_tokens: int = Field(default=4096, description="Maximum token generation limit")
    
    # Memory & Context Settings
    short_term_memory_limit: int = Field(default=50, description="Max short-term memory message slots")
    long_term_memory_limit: int = Field(default=10000, description="Max long-term memory records")
    context_window_size: int = Field(default=128000, description="Context window max token bound")
    context_compression_threshold: float = Field(default=0.8, description="Trigger compression when token ratio hits this threshold")

    # Reasoning & Verification Controls
    enable_self_verification: bool = Field(default=True, description="Enables hallucination and logic verification")
    enable_reflection: bool = Field(default=True, description="Enables pre-response self-critique and improvement")
    max_reflection_loops: int = Field(default=2, description="Maximum internal reflection iterations")
    
    # Provider Configurations Registry (Local Runtimes Active; Commercial APIs Disabled)
    providers: Dict[str, ModelProviderConfig] = Field(
        default_factory=lambda: {
            "ollama": ModelProviderConfig(provider_id="ollama", base_url="http://localhost:11434", default_model="llama3.2:latest", is_local=True, is_enabled=True),
            "llama.cpp": ModelProviderConfig(provider_id="llama.cpp", base_url="http://localhost:8080", default_model="llama-3.2-8b", is_local=True, is_enabled=True),
            "vllm": ModelProviderConfig(provider_id="vllm", base_url="http://localhost:8000", default_model="meta-llama/Llama-3.2-8B", is_local=True, is_enabled=False),
            "openai": ModelProviderConfig(provider_id="openai", base_url="", default_model="disabled", is_local=False, is_enabled=False),
            "anthropic": ModelProviderConfig(provider_id="anthropic", base_url="", default_model="disabled", is_local=False, is_enabled=False),
        }
    )
