"""Abstract base interfaces and contracts for AI Model Integration Platform components.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
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
    PromptTemplate,
    TokenUsage,
    VisionRequest,
    VisionResponse,
)


class IModelProvider(ABC):
    """Unified model provider contract implemented by all local/remote backends."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns provider identifier name."""
        pass

    @abstractmethod
    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Generates text or code completion."""
        pass

    @abstractmethod
    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generates vector embeddings."""
        pass

    @abstractmethod
    async def process_audio(self, request: AudioRequest) -> AudioResponse:
        """Processes STT speech recognition or TTS speech synthesis."""
        pass

    @abstractmethod
    async def process_vision(self, request: VisionRequest) -> VisionResponse:
        """Processes multimodal image/vision analysis."""
        pass


class IModelRegistry(ABC):
    """Universal Model Registry contract."""

    @abstractmethod
    def register_model(self, metadata: ModelMetadata) -> None:
        """Registers model metadata."""
        pass

    @abstractmethod
    def list_models(self) -> List[ModelMetadata]:
        """Lists all registered model metadata."""
        pass

    @abstractmethod
    def get_model(self, model_id: str) -> Optional[ModelMetadata]:
        """Retrieves metadata by model ID."""
        pass

    @abstractmethod
    def find_best_model_for_category(self, category: ModelCategory) -> Optional[ModelMetadata]:
        """Finds highest-priority model for given category."""
        pass



class IModelRouter(ABC):
    """Intelligent Model Router contract."""

    @abstractmethod
    async def route_request(self, request: ModelRoutingRequest) -> ModelRoutingResponse:
        """Selects optimal model and provider based on task category and requirements."""
        pass


class ILocalModelManager(ABC):
    """Local Model Manager contract controlling GGUF, ONNX, PyTorch, Ollama checkpoints."""

    @abstractmethod
    async def load_model(self, model_id: str) -> bool:
        """Loads model into system RAM or GPU VRAM."""
        pass

    @abstractmethod
    async def unload_model(self, model_id: str) -> bool:
        """Unloads model from RAM or GPU VRAM."""
        pass


class IPerformanceManager(ABC):
    """Performance Manager contract controlling VRAM, batching, and GPU allocation."""

    @abstractmethod
    def get_vram_usage(self) -> Dict[str, Any]:
        """Returns GPU VRAM allocation telemetry."""
        pass


class IPromptManager(ABC):
    """Prompt Manager contract versioning prompt templates."""

    @abstractmethod
    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Retrieves versioned prompt template."""
        pass


class IContextManager(ABC):
    """Context Manager contract compressing and summarizing context windows."""

    @abstractmethod
    def compress_context(self, text: str, max_tokens: int = 2048) -> str:
        """Compresses long context text into sliding window summary."""
        pass


class ITokenManager(ABC):
    """Token Manager contract tracking usage and costs."""

    @abstractmethod
    def record_usage(self, usage: TokenUsage) -> None:
        """Logs token usage metrics."""
        pass


class IModelPlatformManager(ABC):
    """Model Platform Manager administrative contract."""

    @abstractmethod
    async def start(self) -> None:
        """Starts model platform engine."""
        pass


class IModelEngine(ABC):
    """Central AI Model Engine facade contract."""

    @abstractmethod
    async def load_model(self, model_id: str) -> bool:
        """Loads model into memory."""
        pass

    @abstractmethod
    async def unload_model(self, model_id: str) -> bool:
        """Unloads model from memory."""
        pass

    @abstractmethod
    async def available_models(self) -> List[ModelMetadata]:
        """Lists available registered models."""
        pass

    @abstractmethod
    async def active_models(self) -> List[ModelMetadata]:
        """Lists active loaded models."""
        pass

    @abstractmethod
    async def route_model(self, category: ModelCategory, prompt: str) -> ModelRoutingResponse:
        """Routes task prompt to optimal model."""
        pass

    @abstractmethod
    async def chat(self, prompt: str, **kwargs: Any) -> GenerationResponse:
        """Generates chat/code response."""
        pass

    @abstractmethod
    async def generate(self, prompt: str, **kwargs: Any) -> GenerationResponse:
        """Generates completion text."""
        pass

    @abstractmethod
    async def embed(self, texts: List[str]) -> EmbeddingResponse:
        """Generates text embeddings."""
        pass

    @abstractmethod
    async def transcribe(self, audio_bytes_or_path: Any) -> AudioResponse:
        """Transcribes speech to text."""
        pass

    @abstractmethod
    async def speak(self, text: str) -> AudioResponse:
        """Synthesizes text to speech."""
        pass

    @abstractmethod
    async def vision(self, image_bytes_or_path: Any, prompt: str = "") -> VisionResponse:
        """Performs visual understanding over image."""
        pass
