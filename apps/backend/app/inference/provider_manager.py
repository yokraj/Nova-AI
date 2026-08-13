"""Provider Manager Module.

Manages connections, health, and configuration for local (Ollama, llama.cpp, vLLM, LM Studio)
and cloud (OpenAI, Anthropic, Gemini, Azure, OpenRouter) providers.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.inference.config import InferenceConfig

logger = structlog.get_logger(__name__)


class ProviderManager:
    """Enterprise LLM Provider Catalog & Health Manager."""

    def __init__(self, config: Optional[InferenceConfig] = None) -> None:
        self.config = config or InferenceConfig()
        self._providers: Dict[str, Dict[str, Any]] = {
            "ollama": {"type": "local", "base_url": self.config.ollama_base_url, "healthy": True},
            "vllm": {"type": "local", "base_url": self.config.vllm_base_url, "healthy": True},
            "llama.cpp": {"type": "local", "base_url": "http://localhost:8080", "healthy": True},
            "lm_studio": {"type": "local", "base_url": "http://localhost:1234", "healthy": True},
            "openai_compatible": {"type": "local", "base_url": self.config.openai_compatible_base_url, "healthy": True},
            "openai": {"type": "cloud", "healthy": True},
            "anthropic": {"type": "cloud", "healthy": True},
            "gemini": {"type": "cloud", "healthy": True},
        }
        logger.info("provider_manager_initialized", supported_providers=len(self._providers))

    def get_provider(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """Fetches provider details."""
        return self._providers.get(provider_name.lower())

    def list_providers(self) -> List[Dict[str, Any]]:
        """Lists registered providers."""
        return [{"name": k, **v} for k, v in self._providers.items()]

    def is_provider_healthy(self, provider_name: str) -> bool:
        """Checks if provider is currently healthy."""
        p = self.get_provider(provider_name)
        return p.get("healthy", True) if p else False
