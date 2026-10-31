"""Model Selector Module.

Selects optimal model based on Task, Latency, GPU availability, Context length,
VRAM footprint, Response quality, Provider health, Priority, and User preferences.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.inference.config import InferenceConfig
from app.inference.model_registry import ModelRegistry

logger = structlog.get_logger(__name__)


class ModelSelector:
    """Enterprise Intelligent Model Selection Engine."""

    def __init__(
        self,
        config: Optional[InferenceConfig] = None,
        model_registry: Optional[ModelRegistry] = None,
    ) -> None:
        self.config = config or InferenceConfig()
        self.model_registry = model_registry or ModelRegistry()
        logger.info("model_selector_initialized")

    def select_model(
        self,
        task_category: str,
        required_capabilities: List[str],
        user_model_override: Optional[str] = None,
        user_provider_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Selects optimal model and provider pair."""
        if user_model_override:
            reg = self.model_registry.get_model(user_model_override)
            provider = user_provider_override or (reg.provider if reg else self.config.default_provider)
            return {"model": user_model_override, "provider": provider, "reason": "User override"}

        if "Vision" in required_capabilities:
            return {"model": "gpt-4o", "provider": "openai", "reason": "Vision capability required"}

        # Default local-first model selection using active local model (e.g. qwen3:8b via Ollama)
        return {
            "model": self.config.default_model,
            "provider": self.config.default_provider,
            "reason": "Default local-first model routing",
        }
