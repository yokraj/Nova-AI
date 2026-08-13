"""Model Dispatcher distributing AI model weights and managing model loads across mesh.
"""

from typing import Any, Dict, List


class ModelDispatcher:
    """Distributes AI model weights and manages model loading across edge devices."""

    def get_loaded_models(self, device_id: str) -> List[Dict[str, Any]]:
        """Returns list of loaded AI models on target device."""
        return [
            {"model_id": "qwen3-8b-instruct", "type": "reasoning", "vram_mb": 5120},
            {"model_id": "faster-whisper-large-v3", "type": "speech", "vram_mb": 3072},
        ]
