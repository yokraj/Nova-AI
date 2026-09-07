"""Central Universal AI Runtime Engine facade unifying local LLM, Speech, TTS, Vision, OCR, Embedding, Translation runtimes.
"""

import time
from typing import Any, AsyncGenerator, List, Optional
from app.ai.runtime.configuration import RuntimeConfiguration
from app.ai.runtime.embedding_runtime import EmbeddingRuntime
from app.ai.runtime.health import RuntimeHealthMonitor
from app.ai.runtime.interfaces import IRuntimeEngine
from app.ai.runtime.llm_runtime import LLMRuntime
from app.ai.runtime.metrics import RuntimeMetricsTracker
from app.ai.runtime.model_downloader import ModelDownloader
from app.ai.runtime.model_profiles import ModelProfilesCatalog
from app.ai.runtime.models import (
    RuntimeHealth,
    RuntimeMetrics,
    RuntimeRequest,
    RuntimeResponse,
)
from app.ai.runtime.ocr_runtime import OCRRuntime
from app.ai.runtime.resource_scheduler import ResourceScheduler
from app.ai.runtime.runtime_cache import RuntimeCache
from app.ai.runtime.runtime_manager import RuntimeManager
from app.ai.runtime.speech_runtime import SpeechRuntime
from app.ai.runtime.translation_runtime import TranslationRuntime
from app.ai.runtime.tts_runtime import TTSRuntime
from app.ai.runtime.vision_runtime import VisionRuntime


class UniversalAIRuntimeEngine(IRuntimeEngine):
    """The central Real AI Runtime Integration Platform runtime for Nova AI."""

    def __init__(self, config: Optional[RuntimeConfiguration] = None) -> None:
        self.config = config or RuntimeConfiguration()
        self.catalog = ModelProfilesCatalog()
        self.scheduler = ResourceScheduler(max_vram_gb=self.config.max_vram_gb, max_ram_gb=self.config.max_ram_gb)
        self.downloader = ModelDownloader()
        self.manager = RuntimeManager(self.scheduler, self.catalog)

        # Specialized runtimes
        self.llm_runtime = LLMRuntime()
        self.speech_runtime = SpeechRuntime()
        self.tts_runtime = TTSRuntime()
        self.vision_runtime = VisionRuntime()
        self.ocr_runtime = OCRRuntime()
        self.embedding_runtime = EmbeddingRuntime()
        self.translation_runtime = TranslationRuntime()

        # Telemetry & intelligent cache
        self.metrics_tracker = RuntimeMetricsTracker()
        self.health_monitor = RuntimeHealthMonitor()
        self.cache = RuntimeCache(ttl_seconds=self.config.cache_ttl_seconds)

    async def chat(self, prompt: str, **kwargs: Any) -> RuntimeResponse:
        """Executes LLM chat generation with intelligent caching."""
        cache_key = f"chat:{prompt}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        req = RuntimeRequest(model_id=kwargs.get("model_id", "qwen3:8b"), prompt=prompt)
        res = await self.llm_runtime.generate(req)
        self.metrics_tracker.record_inference(is_local=True, latency_ms=res.latency_ms, tokens=res.token_usage.get("total_tokens", 50))
        self.cache.set(cache_key, res)
        return res

    async def chat_stream(self, prompt: str, **kwargs: Any) -> AsyncGenerator[str, None]:
        """Streams LLM chat tokens."""
        req = RuntimeRequest(model_id=kwargs.get("model_id", "qwen3:8b"), prompt=prompt)
        async for chunk in self.llm_runtime.generate_stream(req):
            yield chunk

    async def reason(self, prompt: str, **kwargs: Any) -> RuntimeResponse:
        """Executes deep reasoning inference with caching."""
        cache_key = f"reason:{prompt}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        req = RuntimeRequest(model_id=kwargs.get("model_id", "qwen3:8b"), prompt=prompt)
        res = await self.llm_runtime.generate(req)
        self.metrics_tracker.record_inference(is_local=True, latency_ms=res.latency_ms, tokens=res.token_usage.get("total_tokens", 50))
        self.cache.set(cache_key, res)
        return res

    async def code(self, prompt: str, **kwargs: Any) -> RuntimeResponse:
        """Executes code generation inference with caching."""
        cache_key = f"code:{prompt}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        req = RuntimeRequest(model_id=kwargs.get("model_id", "deepseek-coder:6.7b"), prompt=prompt)
        res = await self.llm_runtime.generate(req)
        self.metrics_tracker.record_inference(is_local=True, latency_ms=res.latency_ms, tokens=res.token_usage.get("total_tokens", 50))
        self.cache.set(cache_key, res)
        return res

    async def vision(self, image_bytes_or_path: Any, prompt: str = "", **kwargs: Any) -> RuntimeResponse:
        """Executes multimodal visual reasoning."""
        cache_key = f"vision:{prompt}:{str(image_bytes_or_path)[:50]}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        res = await self.vision_runtime.process_vision(image_bytes_or_path, prompt=prompt)
        self.metrics_tracker.record_inference(is_local=True, latency_ms=res.latency_ms, tokens=40)
        self.cache.set(cache_key, res)
        return res

    async def transcribe(self, audio_bytes_or_path: Any) -> RuntimeResponse:
        """Executes speech-to-text transcription."""
        res = await self.speech_runtime.transcribe(audio_bytes_or_path)
        self.metrics_tracker.record_inference(is_local=True, latency_ms=res.latency_ms, tokens=12)
        return res

    async def speak(self, text: str) -> RuntimeResponse:
        """Executes text-to-speech synthesis."""
        res = await self.tts_runtime.speak(text)
        self.metrics_tracker.record_inference(is_local=True, latency_ms=res.latency_ms, tokens=len(text.split()))
        return res

    async def tts(self, text: str) -> RuntimeResponse:
        """Alias for speak text-to-speech synthesis."""
        return await self.speak(text)

    async def embed(self, texts: List[str]) -> RuntimeResponse:
        """Executes dense vector embeddings generation."""
        cache_key = f"embed:{hash(tuple(texts))}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        res = await self.embedding_runtime.embed(texts)
        self.metrics_tracker.record_inference(is_local=True, latency_ms=res.latency_ms, tokens=len(texts) * 10)
        self.cache.set(cache_key, res)
        return res

    async def ocr(self, image_bytes_or_path: Any) -> RuntimeResponse:
        """Executes document OCR text extraction."""
        res = await self.ocr_runtime.ocr(image_bytes_or_path)
        self.metrics_tracker.record_inference(is_local=True, latency_ms=res.latency_ms, tokens=30)
        return res

    async def translate(self, text: str, source_lang: str = "auto", target_lang: str = "es") -> RuntimeResponse:
        """Executes neural text translation."""
        res = await self.translation_runtime.translate(text, source_lang, target_lang)
        self.metrics_tracker.record_inference(is_local=True, latency_ms=res.latency_ms, tokens=len(text.split()))
        return res

    async def load_runtime(self, model_id: str) -> bool:
        """Loads model into active runtime memory."""
        return await self.manager.load_model(model_id)

    async def runtime_status(self) -> RuntimeHealth:
        """Retrieves runtime health status."""
        return self.health_monitor.check_health(self.manager.list_active_models())

    async def active_models(self) -> List[str]:
        """Lists active models."""
        return self.manager.list_active_models()

    async def get_metrics(self) -> Any:
        """Retrieves runtime platform telemetry metrics."""
        return self.metrics_tracker.get_metrics()


