"""Universal Model Registry managing registered models, capabilities, quantization, auto-discovery, and priorities.
"""

from typing import Any, Dict, List, Optional
from app.ai.models.interfaces import IModelRegistry
from app.ai.models.models import (
    ModelCapability,
    ModelCategory,
    ModelMetadata,
    ModelStatus,
)


class UniversalModelRegistry(IModelRegistry):
    """Universal Model Registry storing metadata, GPU/RAM requirements, and versioning with dynamic capability discovery."""

    def __init__(self) -> None:
        self._registry: Dict[str, ModelMetadata] = self._seed_default_models()

    def _seed_default_models(self) -> Dict[str, ModelMetadata]:
        defaults = [
            ModelMetadata(
                model_id="qwen3:8b",
                name="Qwen 3 8B Instruct Reasoning",
                category=ModelCategory.REASONING,
                capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.REASONING],
                provider_type="ollama",
                quantization="Q4_K_M",
                vram_mb=5120,
                priority=10,
            ),
            ModelMetadata(
                model_id="deepseek-coder:6.7b",
                name="DeepSeek Coder 6.7B",
                category=ModelCategory.CODING,
                capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.TEXT_GENERATION],
                provider_type="ollama",
                quantization="Q4_K_M",
                vram_mb=4096,
                priority=10,
            ),
            ModelMetadata(
                model_id="qwen2.5-vl:7b",
                name="Qwen 2.5 VL 7B",
                category=ModelCategory.VISION,
                capabilities=[ModelCapability.VISION_UNDERSTANDING, ModelCapability.TEXT_GENERATION],
                provider_type="ollama",
                quantization="Q4_K_M",
                vram_mb=5120,
                priority=9,
            ),
            ModelMetadata(
                model_id="whisper-large-v3",
                name="OpenAI Whisper Large v3",
                category=ModelCategory.SPEECH,
                capabilities=[ModelCapability.SPEECH_TO_TEXT],
                provider_type="whisper",
                quantization="FP16",
                vram_mb=3072,
                priority=10,
            ),
            ModelMetadata(
                model_id="piper-en-tts",
                name="Piper Fast Local TTS",
                category=ModelCategory.TTS,
                capabilities=[ModelCapability.TEXT_TO_SPEECH],
                provider_type="piper",
                quantization="INT8",
                vram_mb=512,
                priority=10,
            ),
            ModelMetadata(
                model_id="bge-large-en-v1.5",
                name="BGE Large English Embeddings",
                category=ModelCategory.EMBEDDING,
                capabilities=[ModelCapability.EMBEDDINGS],
                provider_type="bge_embedding",
                quantization="FP32",
                vram_mb=1024,
                priority=10,
            ),
            ModelMetadata(
                model_id="paddleocr-v4",
                name="PaddleOCR Document OCR",
                category=ModelCategory.OCR,
                capabilities=[ModelCapability.OCR],
                provider_type="paddleocr",
                quantization="INT8",
                vram_mb=1024,
                priority=10,
            ),
        ]
        return {m.model_id: m for m in defaults}

    def register_model(self, metadata: ModelMetadata) -> None:
        """Registers a new model in the registry."""
        self._registry[metadata.model_id] = metadata

    def list_models(self) -> List[ModelMetadata]:
        """Lists all registered model metadata."""
        return list(self._registry.values())

    def get_model(self, model_id: str) -> Optional[ModelMetadata]:
        """Retrieves model metadata by model ID."""
        return self._registry.get(model_id)

    def find_best_model_for_category(self, category: ModelCategory) -> Optional[ModelMetadata]:
        """Finds highest-priority model for given category."""
        matching = [m for m in self.list_models() if m.category == category]
        if matching:
            matching.sort(key=lambda m: m.priority, reverse=True)
            return matching[0]
        all_models = self.list_models()
        return all_models[0] if all_models else None


    async def discover_ollama_capabilities(self, installed_ollama_models: List[Dict[str, Any]]) -> List[ModelMetadata]:
        """Auto-discovers installed Ollama models and registers their capabilities dynamically."""
        discovered: List[ModelMetadata] = []
        for model in installed_ollama_models:
            name = model.get("name", "")
            size_mb = model.get("size", 4000000000) // (1024 * 1024)

            category = ModelCategory.REASONING
            capabilities = [ModelCapability.TEXT_GENERATION]

            if "coder" in name.lower() or "code" in name.lower():
                category = ModelCategory.CODING
                capabilities.append(ModelCapability.CODE_GENERATION)
            elif "vl" in name.lower() or "vision" in name.lower():
                category = ModelCategory.VISION
                capabilities.append(ModelCapability.VISION_UNDERSTANDING)
            elif "embed" in name.lower() or "bge" in name.lower():
                category = ModelCategory.EMBEDDING
                capabilities.append(ModelCapability.EMBEDDINGS)

            meta = ModelMetadata(
                model_id=name,
                name=f"Discovered {name}",
                category=category,
                capabilities=capabilities,
                provider_type="ollama",
                quantization="Q4_K_M",
                vram_mb=max(2048, size_mb),
                priority=8,
            )
            self.register_model(meta)
            discovered.append(meta)
        return discovered
