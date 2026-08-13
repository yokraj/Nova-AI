"""Abstract base interfaces and contracts for Universal AI Orchestrator.
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, List, Optional
from app.ai.orchestrator.models import (
    BenchmarkScore,
    GPUTelemetry,
    ModelDownloadProgress,
    ModelSpec,
    OrchestratorHealth,
    OrchestratorRequest,
    OrchestratorResponse,
    RoutingContext,
    RoutingDecision,
    StreamTokenChunk,
)


class IProviderPlugin(ABC):
    """Contract for modular AI provider plugins (Ollama, llama.cpp, Whisper, Piper, etc.)."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of provider adapter."""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Verifies if backend daemon or library is reachable."""
        pass

    @abstractmethod
    async def generate(self, request: OrchestratorRequest) -> OrchestratorResponse:
        """Executes text/data generation request."""
        pass

    @abstractmethod
    async def generate_stream(self, request: OrchestratorRequest) -> AsyncGenerator[StreamTokenChunk, None]:
        """Streams real-time token chunks."""
        pass


class IIntelligentModelRouter(ABC):
    """Contract for task-based multi-factor model router."""

    @abstractmethod
    def route_request(self, context: RoutingContext) -> RoutingDecision:
        """Calculates optimal model selection based on hardware, quality, latency, and context."""
        pass


class IGPUScheduler(ABC):
    """Contract for hardware GPU/VRAM resource manager."""

    @abstractmethod
    def get_telemetry(self) -> GPUTelemetry:
        """Snapshot current GPU, VRAM, RAM, and CPU metrics."""
        pass

    @abstractmethod
    async def prepare_resource(self, model_id: str, required_vram_mb: int) -> bool:
        """Ensures VRAM allocation safety and unloads idle models if near OOM limit."""
        pass


class IModelInstaller(ABC):
    """Contract for automatic model downloader and installer."""

    @abstractmethod
    async def check_missing_model(self, model_id: str) -> bool:
        """Checks if model weights exist locally."""
        pass

    @abstractmethod
    async def install_model(self, model_id: str) -> ModelDownloadProgress:
        """Downloads, verifies SHA-256, and installs model weights."""
        pass


class IBenchmarkEngine(ABC):
    """Contract for automated model benchmarking."""

    @abstractmethod
    async def benchmark_model(self, model_id: str) -> BenchmarkScore:
        """Runs automated speed, throughput, memory, and accuracy benchmark."""
        pass

    @abstractmethod
    def get_benchmark_score(self, model_id: str) -> Optional[BenchmarkScore]:
        """Retrieves cached historical benchmark score."""
        pass


class IPromptOptimizer(ABC):
    """Contract for template-based prompt optimization."""

    @abstractmethod
    def optimize_prompt(self, prompt: str, category: str, variables: Optional[Dict[str, Any]] = None) -> str:
        """Enriches raw prompt with specialized domain template."""
        pass


class IStreamingEngine(ABC):
    """Contract for provider-agnostic token streaming runtime."""

    @abstractmethod
    async def stream_tokens(self, request: OrchestratorRequest) -> AsyncGenerator[StreamTokenChunk, None]:
        """Streams tokens with pause, cancellation, and barge-in support."""
        pass


class IUniversalAIOrchestratorEngine(ABC):
    """Unified single-source-of-truth contract for every Nova AI subsystem."""

    @abstractmethod
    async def chat(self, prompt: str, **kwargs: Any) -> OrchestratorResponse:
        """Multi-turn conversation inference API."""
        pass

    @abstractmethod
    async def reason(self, prompt: str, **kwargs: Any) -> OrchestratorResponse:
        """Deep reasoning and architectural analysis API."""
        pass

    @abstractmethod
    async def code(self, prompt: str, **kwargs: Any) -> OrchestratorResponse:
        """Software copilot code generation and refactoring API."""
        pass

    @abstractmethod
    async def vision(self, image_path_or_bytes: Any, prompt: str = "", **kwargs: Any) -> OrchestratorResponse:
        """Multimodal visual reasoning API."""
        pass

    @abstractmethod
    async def transcribe(self, audio_bytes_or_path: Any, **kwargs: Any) -> OrchestratorResponse:
        """Speech-to-text transcription API."""
        pass

    @abstractmethod
    async def tts(self, text: str, **kwargs: Any) -> OrchestratorResponse:
        """Text-to-speech voice synthesis API."""
        pass

    @abstractmethod
    async def embed(self, texts: List[str], **kwargs: Any) -> OrchestratorResponse:
        """Dense vector embedding generation API."""
        pass

    @abstractmethod
    async def translate(self, text: str, target_lang: str = "en", **kwargs: Any) -> OrchestratorResponse:
        """Machine translation API."""
        pass

    @abstractmethod
    async def ocr(self, image_bytes_or_path: Any, **kwargs: Any) -> OrchestratorResponse:
        """Screen and document OCR extraction API."""
        pass

    @abstractmethod
    async def plan(self, goal: str, **kwargs: Any) -> OrchestratorResponse:
        """Goal DAG planning API."""
        pass

    @abstractmethod
    async def summarize(self, text: str, **kwargs: Any) -> OrchestratorResponse:
        """Content summarization API."""
        pass

    @abstractmethod
    async def analyze(self, data: Any, **kwargs: Any) -> OrchestratorResponse:
        """Unified analytical reasoning API."""
        pass

    @abstractmethod
    async def stream(self, prompt: str, **kwargs: Any) -> AsyncGenerator[StreamTokenChunk, None]:
        """Universal streaming token stream API."""
        pass
