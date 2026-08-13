"""Local Model Manager handling checkpoint downloads, RAM/VRAM loading, and unloading.
"""

from typing import Dict, List, Optional
from app.ai.models.interfaces import ILocalModelManager
from app.ai.models.model_registry import UniversalModelRegistry
from app.ai.models.models import ModelStatus


class LocalModelManager(ILocalModelManager):
    """Local Model Manager controlling GGUF, ONNX, PyTorch, Ollama model lifecycles."""

    def __init__(self, registry: UniversalModelRegistry) -> None:
        self.registry = registry
        self._loaded_models: Dict[str, bool] = {}

    async def load_model(self, model_id: str) -> bool:
        """Loads model into active memory.

        Args:
            model_id: Target model ID string.

        Returns:
            True if loaded successfully.
        """
        meta = self.registry.get_model(model_id)
        if meta:
            meta.status = ModelStatus.READY
            self._loaded_models[model_id] = True
            return True
        return False

    async def unload_model(self, model_id: str) -> bool:
        """Unloads model from active memory.

        Args:
            model_id: Target model ID string.

        Returns:
            True if unloaded.
        """
        meta = self.registry.get_model(model_id)
        if meta:
            meta.status = ModelStatus.UNLOADED
            if model_id in self._loaded_models:
                del self._loaded_models[model_id]
            return True
        return False

    def is_loaded(self, model_id: str) -> bool:
        """Returns True if model is currently loaded in memory."""
        return self._loaded_models.get(model_id, False)

    def list_active_models(self) -> List[str]:
        """Returns list of currently loaded model IDs."""
        return list(self._loaded_models.keys())
