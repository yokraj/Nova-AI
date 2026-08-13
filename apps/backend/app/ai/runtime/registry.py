"""Registry tracking metadata of local models.
"""

from typing import Dict, List, Optional
from app.ai.runtime.models import LocalModelInfo, ModelCapability

class LocalModelRegistry:
    """Manages metadata for local models and tracks loaded status."""

    def __init__(self) -> None:
        self._models: Dict[str, LocalModelInfo] = {}
        self._default_models = {
            "qwen2.5-coder": LocalModelInfo(
                id="qwen2.5-coder",
                name="qwen2.5-coder",
                provider="ollama",
                type="llm",
                context_window=32768,
                parameters="7B",
                quantization="q4_K_M",
                loaded_status=False
            ),
            "deepseek-r1-distill-qwen": LocalModelInfo(
                id="deepseek-r1-distill-qwen",
                name="deepseek-r1-distill-qwen",
                provider="ollama",
                type="llm",
                context_window=16384,
                parameters="8B",
                quantization="q4_K_M",
                loaded_status=False
            ),
            "nomic-embed-text": LocalModelInfo(
                id="nomic-embed-text",
                name="nomic-embed-text",
                provider="ollama",
                type="embedding",
                context_window=8192,
                parameters="137M",
                quantization="fp16",
                loaded_status=False
            ),
            "qwen2.5-vl": LocalModelInfo(
                id="qwen2.5-vl",
                name="qwen2.5-vl",
                provider="ollama",
                type="multimodal",
                context_window=16384,
                parameters="7B",
                quantization="q4_K_M",
                loaded_status=False
            )
        }
        # Pre-populate registry with default local models
        for name, info in self._default_models.items():
            self.register_model(info)

    def register_model(self, model: LocalModelInfo) -> None:
        """Adds a local model to registry."""
        self._models[model.name] = model

    def get_model(self, name: str) -> Optional[LocalModelInfo]:
        """Fetches metadata configuration for a local model."""
        return self._models.get(name)

    def list_models(self) -> List[LocalModelInfo]:
        """Returns all registered local models."""
        return list(self._models.values())
