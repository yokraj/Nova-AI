"""Model Registry Module.

Manages catalog of registered local and cloud AI models with capabilities,
context windows, VRAM requirements, and operational status.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.inference.schemas import ModelCatalogItem

logger = structlog.get_logger(__name__)


class ModelRegistry:
    """Enterprise AI Model Catalog & Capability Registry."""

    def __init__(self) -> None:
        self._models: Dict[str, Dict[str, Any]] = {}
        self._bootstrap_default_models()
        logger.info("model_registry_initialized", registered_count=len(self._models))

    def _bootstrap_default_models(self) -> None:
        """Registers default local and cloud AI models.
        
        Under Zero-Cost Policy, all commercial cloud models are strictly marked is_active=False.
        """
        defaults = [
            {
                "model_name": "qwen3:8b",
                "provider": "ollama",
                "context_window": 32768,
                "supports_vision": False,
                "supports_function_calling": True,
                "supports_streaming": True,
                "vram_required_mb": 5120,
                "is_active": True,
            },
            {
                "model_name": "qwen2.5-coder",
                "provider": "ollama",
                "context_window": 32768,
                "supports_vision": False,
                "supports_function_calling": True,
                "supports_streaming": True,
                "vram_required_mb": 5120,
                "is_active": True,
            },
            {
                "model_name": "llama3.2",
                "provider": "ollama",
                "context_window": 131072,
                "supports_vision": False,
                "supports_function_calling": True,
                "supports_streaming": True,
                "vram_required_mb": 4096,
                "is_active": True,
            },
            {
                "model_name": "deepseek-r1-distill-qwen",
                "provider": "ollama",
                "context_window": 16384,
                "supports_vision": False,
                "supports_function_calling": True,
                "supports_streaming": True,
                "vram_required_mb": 5120,
                "is_active": True,
            },
            {
                "model_name": "qwen2.5-vl",
                "provider": "ollama",
                "context_window": 16384,
                "supports_vision": True,
                "supports_function_calling": True,
                "supports_streaming": True,
                "vram_required_mb": 5120,
                "is_active": True,
            },
            {
                "model_name": "llama3.1:70b",
                "provider": "vllm",
                "context_window": 131072,
                "supports_vision": False,
                "supports_function_calling": True,
                "supports_streaming": True,
                "vram_required_mb": 24576,
                "is_active": False,
            },
            {
                "model_name": "gpt-4o",
                "provider": "openai",
                "context_window": 128000,
                "supports_vision": True,
                "supports_function_calling": True,
                "supports_streaming": True,
                "vram_required_mb": 0,
                "is_active": False,  # Disabled under Zero-Cost Policy
            },
            {
                "model_name": "claude-3-5-sonnet",
                "provider": "anthropic",
                "context_window": 200000,
                "supports_vision": True,
                "supports_function_calling": True,
                "supports_streaming": True,
                "vram_required_mb": 0,
                "is_active": False,  # Disabled under Zero-Cost Policy
            },
        ]
        for m in defaults:
            self._models[m["model_name"]] = m

    def register_model(self, model_data: Dict[str, Any]) -> ModelCatalogItem:
        """Registers a new model in catalog."""
        name = model_data["model_name"]
        self._models[name] = model_data
        logger.info("model_registered", model_name=name, provider=model_data.get("provider"))
        return ModelCatalogItem(**model_data)

    def get_model(self, model_name: str) -> Optional[ModelCatalogItem]:
        """Fetches model item by name."""
        m = self._models.get(model_name)
        if not m:
            return None
        return ModelCatalogItem(**m)

    def list_models(self, active_only: bool = True) -> List[ModelCatalogItem]:
        """Lists registered models."""
        items = list(self._models.values())
        if active_only:
            items = [m for m in items if m.get("is_active", True)]
        return [ModelCatalogItem(**m) for m in items]
