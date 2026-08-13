"""Central AI Model Engine orchestrating multi-model inference, intelligent routing, and providers.
"""

import time
from typing import Any, Dict, List, Optional
from app.ai.models.configuration import ModelPlatformConfiguration
from app.ai.models.context_manager import ContextManager
from app.ai.models.health import ModelHealthMonitor
from app.ai.models.interfaces import IModelEngine, IModelProvider
from app.ai.models.local_model_manager import LocalModelManager
from app.ai.models.metrics import ModelMetricsTracker
from app.ai.models.model_manager import ModelPlatformManager
from app.ai.models.model_registry import UniversalModelRegistry
from app.ai.models.model_router import IntelligentModelRouter
from app.ai.models.models import (
    AudioRequest,
    AudioResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    GenerationRequest,
    GenerationResponse,
    ModelCategory,
    ModelHealth,
    ModelMetadata,
    ModelMetrics,
    ModelRoutingRequest,
    ModelRoutingResponse,
    TokenUsage,
    VisionRequest,
    VisionResponse,
)
from app.ai.models.performance_manager import PerformanceManager
from app.ai.models.prompt_manager import PromptManager
from app.ai.models.providers import (
    AnthropicProvider,
    EmbeddingProvider,
    GeminiProvider,
    LlamaCppProvider,
    OllamaProvider,
    OpenAIProvider,
    PaddleOCRProvider,
    PiperProvider,
    TransformersProvider,
    WhisperProvider,
)
from app.ai.models.mock_provider import MockModelProvider
from app.ai.models.token_manager import TokenManager


class AIModelEngine(IModelEngine):
    """The central Universal AI Model Integration Platform runtime for Nova AI."""

    def __init__(self, config: Optional[ModelPlatformConfiguration] = None) -> None:
        self.config = config or ModelPlatformConfiguration()
        self.manager = ModelPlatformManager(self.config)
        self.registry = UniversalModelRegistry()
        self.router = IntelligentModelRouter(self.registry)
        self.local_manager = LocalModelManager(self.registry)
        self.performance_manager = PerformanceManager(max_vram_gb=self.config.max_vram_gb)
        self.prompt_manager = PromptManager()
        self.context_manager = ContextManager()
        self.token_manager = TokenManager()
        self.metrics_tracker = ModelMetricsTracker()
        self.health_monitor = ModelHealthMonitor()

        # Initialize provider registry
        self.providers: Dict[str, IModelProvider] = {
            "ollama": OllamaProvider(),
            "llamacpp": LlamaCppProvider(),
            "transformers": TransformersProvider(),
            "whisper": WhisperProvider(),
            "piper": PiperProvider(),
            "paddleocr": PaddleOCRProvider(),
            "bge_embedding": EmbeddingProvider(),
            "openai": OpenAIProvider(),
            "gemini": GeminiProvider(),
            "anthropic": AnthropicProvider(),
            "mock_provider": MockModelProvider(),
        }

    async def load_model(self, model_id: str) -> bool:
        """Loads model into active memory."""
        meta = self.registry.get_model(model_id)
        if meta:
            allocated = self.performance_manager.allocate_vram(meta.vram_mb)
            if allocated:
                return await self.local_manager.load_model(model_id)
        return False

    async def unload_model(self, model_id: str) -> bool:
        """Unloads model from active memory."""
        meta = self.registry.get_model(model_id)
        if meta:
            self.performance_manager.release_vram(meta.vram_mb)
            return await self.local_manager.unload_model(model_id)
        return False

    async def available_models(self) -> List[ModelMetadata]:
        """Lists all registered models."""
        return self.registry.list_models()

    async def active_models(self) -> List[ModelMetadata]:
        """Lists currently loaded models."""
        active_ids = self.local_manager.list_active_models()
        return [m for m in self.registry.list_models() if m.model_id in active_ids]

    async def route_model(self, category: ModelCategory, prompt: str) -> ModelRoutingResponse:
        """Routes prompt to optimal model based on task category."""
        req = ModelRoutingRequest(task_category=category, prompt=prompt)
        return await self.router.route_request(req)

    async def generate(self, prompt: str, **kwargs: Any) -> GenerationResponse:
        """Generates completion text using routed model."""
        start_time = time.time()
        category = kwargs.get("category", ModelCategory.CODING if "code" in prompt.lower() else ModelCategory.GENERAL)
        route = await self.route_model(category, prompt)

        provider = self.providers.get(route.provider_type, self.providers["ollama"])
        req = GenerationRequest(
            prompt=prompt,
            model_id=route.selected_model_id,
            max_tokens=kwargs.get("max_tokens", 1024),
            temperature=kwargs.get("temperature", 0.7),
        )

        res = await provider.generate(req)
        self.token_manager.record_usage(res.token_usage)
        elapsed_ms = (time.time() - start_time) * 1000.0
        self.metrics_tracker.record_routing_request(
            is_local=route.provider_type not in ["openai", "gemini", "anthropic"],
            latency_ms=elapsed_ms,
            tokens=res.token_usage.total_tokens,
            fallback=route.fallback_used,
        )
        return res

    async def chat(self, prompt: str, **kwargs: Any) -> GenerationResponse:
        """Generates chat/code response."""
        return await self.generate(prompt, **kwargs)

    async def embed(self, texts: List[str]) -> EmbeddingResponse:
        """Generates text vector embeddings."""
        route = await self.route_model(ModelCategory.EMBEDDING, texts[0] if texts else "")
        provider = self.providers.get(route.provider_type, self.providers["bge_embedding"])
        req = EmbeddingRequest(text_list=texts, model_id=route.selected_model_id)
        return await provider.embed(req)

    async def transcribe(self, audio_bytes_or_path: Any) -> AudioResponse:
        """Transcribes speech audio to text."""
        route = await self.route_model(ModelCategory.SPEECH, "transcribe audio")
        provider = self.providers.get(route.provider_type, self.providers["whisper"])
        req = AudioRequest(audio_bytes_or_path=audio_bytes_or_path, task_type="transcribe")
        return await provider.process_audio(req)

    async def speak(self, text: str) -> AudioResponse:
        """Synthesizes text to speech audio."""
        route = await self.route_model(ModelCategory.TTS, text)
        provider = self.providers.get(route.provider_type, self.providers["piper"])
        req = AudioRequest(audio_bytes_or_path=text, task_type="speak")
        return await provider.process_audio(req)

    async def vision(self, image_bytes_or_path: Any, prompt: str = "") -> VisionResponse:
        """Performs visual understanding over an image."""
        route = await self.route_model(ModelCategory.VISION, prompt or "analyze image")
        provider = self.providers.get(route.provider_type, self.providers["ollama"])
        req = VisionRequest(image_bytes_or_path=image_bytes_or_path, prompt=prompt)
        return await provider.process_vision(req)

    async def check_health(self) -> ModelHealth:
        """Retrieves model platform health diagnostics."""
        active_ids = self.local_manager.list_active_models()
        vram_info = self.performance_manager.get_vram_usage()
        return self.health_monitor.check_health(active_ids, int(vram_info["used_vram_mb"]))

    async def get_metrics(self) -> ModelMetrics:
        """Retrieves model platform telemetry metrics."""
        return self.metrics_tracker.get_metrics()
