"""Model Profiles Catalog defining capabilities, VRAM/RAM specs, context limits, and licenses.
"""

from typing import Dict, List, Optional
from app.ai.runtime.models import ModelProfile, ModelType, QuantType


class ModelProfilesCatalog:
    """Catalog of local AI model specifications and recommended task configurations."""

    def __init__(self) -> None:
        self._profiles: Dict[str, ModelProfile] = self._seed_catalog()

    def _seed_catalog(self) -> Dict[str, ModelProfile]:
        profiles = [
            ModelProfile(
                model_id="qwen3-8b-instruct",
                name="Qwen 3 8B Instruct",
                type=ModelType.REASONING,
                quant=QuantType.GGUF_Q4_K_M,
                min_vram_mb=5120,
                min_ram_mb=8192,
                context_length=32768,
                recommended_tasks=["general reasoning", "complex planning", "decision making"],
                license="Apache-2.0",
            ),
            ModelProfile(
                model_id="deepseek-coder-v2-lite",
                name="DeepSeek Coder V2 Lite",
                type=ModelType.CODING,
                quant=QuantType.GGUF_Q4_K_M,
                min_vram_mb=4096,
                min_ram_mb=8192,
                context_length=16384,
                recommended_tasks=["python coding", "refactoring", "bug fixing", "architecture"],
                license="MIT",
            ),
            ModelProfile(
                model_id="qwen2.5-vl-7b",
                name="Qwen 2.5 Vision Language 7B",
                type=ModelType.VISION,
                quant=QuantType.GGUF_Q4_K_M,
                min_vram_mb=5120,
                min_ram_mb=8192,
                context_length=8192,
                recommended_tasks=["gui understanding", "chart reasoning", "visual groundings"],
                license="Apache-2.0",
            ),
            ModelProfile(
                model_id="faster-whisper-large-v3",
                name="Faster Whisper Large v3",
                type=ModelType.SPEECH,
                quant=QuantType.FP16,
                min_vram_mb=3072,
                min_ram_mb=4096,
                context_length=4096,
                recommended_tasks=["realtime transcription", "streaming stt", "language detection"],
                license="MIT",
            ),
            ModelProfile(
                model_id="piper-kokoro-tts",
                name="Piper / Kokoro Fast Local TTS",
                type=ModelType.TTS,
                quant=QuantType.INT8,
                min_vram_mb=512,
                min_ram_mb=2048,
                context_length=2048,
                recommended_tasks=["streaming speech synthesis", "voice profiles", "voice response"],
                license="MIT",
            ),
            ModelProfile(
                model_id="paddleocr-v4-local",
                name="PaddleOCR Document OCR Engine",
                type=ModelType.OCR,
                quant=QuantType.INT8,
                min_vram_mb=1024,
                min_ram_mb=2048,
                context_length=4096,
                recommended_tasks=["pdf ocr", "table extraction", "form layout detection"],
                license="Apache-2.0",
            ),
            ModelProfile(
                model_id="bge-m3-embeddings",
                name="BGE M3 Vector Embeddings",
                type=ModelType.EMBEDDING,
                quant=QuantType.FP32,
                min_vram_mb=1024,
                min_ram_mb=2048,
                context_length=8192,
                recommended_tasks=["batch embeddings", "vector retrieval", "semantic similarity"],
                license="MIT",
            ),
            ModelProfile(
                model_id="nllb-200-translation",
                name="NLLB 200 Multi-Language Translator",
                type=ModelType.TRANSLATION,
                quant=QuantType.FP16,
                min_vram_mb=2048,
                min_ram_mb=4096,
                context_length=4096,
                recommended_tasks=["multi-language translation", "document translation"],
                license="Creative Commons NC",
            ),
        ]
        return {p.model_id: p for p in profiles}

    def get_profile(self, model_id: str) -> Optional[ModelProfile]:
        """Retrieves profile specs by model ID."""
        return self._profiles.get(model_id)

    def list_profiles(self) -> List[ModelProfile]:
        """Lists all registered model profiles."""
        return list(self._profiles.values())
