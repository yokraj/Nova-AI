"""Abstract base interfaces and contracts for Real AI Runtime Integration & Execution Platform.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from app.ai.runtime.models import (
    DeviceType,
    DownloadProgress,
    ModelProfile,
    ResourceTelemetry,
    RuntimeHealth,
    RuntimeMetrics,
    RuntimeRequest,
    RuntimeResponse,
    StreamChunkResponse,
)


class ILLMRuntime(ABC):
    """LLM Runtime contract for text generation, code completion, and tool calling."""

    @abstractmethod
    async def generate(self, request: RuntimeRequest) -> RuntimeResponse:
        """Executes text generation request."""
        pass


class ISpeechRuntime(ABC):
    """Speech Runtime contract for speech-to-text transcription."""

    @abstractmethod
    async def transcribe(self, audio_bytes_or_path: Any) -> RuntimeResponse:
        """Transcribes audio input to text."""
        pass


class ITTSRuntime(ABC):
    """Voice Runtime contract for text-to-speech synthesis."""

    @abstractmethod
    async def speak(self, text: str) -> RuntimeResponse:
        """Synthesizes text input to audio waveform."""
        pass


class IVisionRuntime(ABC):
    """Vision Runtime contract for multimodal image understanding."""

    @abstractmethod
    async def process_vision(self, image_bytes_or_path: Any, prompt: str = "") -> RuntimeResponse:
        """Performs visual reasoning over an image."""
        pass


class IOCRRuntime(ABC):
    """OCR Runtime contract for document and screen text recognition."""

    @abstractmethod
    async def process_ocr(self, image_bytes_or_path: Any) -> RuntimeResponse:
        """Extracts text, tables, and layouts from image or PDF."""
        pass


class IEmbeddingRuntime(ABC):
    """Embedding Runtime contract for vector generation."""

    @abstractmethod
    async def embed(self, texts: List[str]) -> RuntimeResponse:
        """Generates text vector embeddings."""
        pass


class ITranslationRuntime(ABC):
    """Translation Runtime contract for multi-language text translation."""

    @abstractmethod
    async def translate(self, text: str, target_lang: str = "en") -> RuntimeResponse:
        """Translates input text into target language."""
        pass


class IRuntimeManager(ABC):
    """Runtime Manager contract controlling model load/unload states."""

    @abstractmethod
    async def load_model(self, model_id: str) -> bool:
        """Loads model into active GPU/RAM memory."""
        pass

    @abstractmethod
    async def unload_model(self, model_id: str) -> bool:
        """Unloads model from active memory."""
        pass

    @abstractmethod
    def list_active_models(self) -> List[str]:
        """Lists currently loaded model IDs."""
        pass


class IResourceScheduler(ABC):
    """Resource Scheduler contract tracking VRAM and RAM allocation."""

    @abstractmethod
    def get_telemetry(self) -> ResourceTelemetry:
        """Retrieves hardware resource allocation snapshot."""
        pass


class IModelDownloader(ABC):
    """Model Downloader contract downloading and verifying model weights."""

    @abstractmethod
    async def download_model(self, model_id: str) -> DownloadProgress:
        """Downloads model weights with checksum verification."""
        pass


class IRuntimeCache(ABC):
    """Runtime Cache contract managing multi-modal inference cache."""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Retrieves cached item."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """Caches item with TTL timestamp."""
        pass


class IRuntimeMonitor(ABC):
    """Runtime Monitor contract collecting latency and hardware telemetry."""

    @abstractmethod
    def check_health(self) -> RuntimeHealth:
        """Performs health check diagnostic."""
        pass


class IRuntimeEngine(ABC):
    """Central Universal AI Runtime Engine facade contract."""

    @abstractmethod
    async def chat(self, prompt: str, **kwargs: Any) -> RuntimeResponse:
        """Executes LLM chat completion."""
        pass

    @abstractmethod
    async def reason(self, prompt: str, **kwargs: Any) -> RuntimeResponse:
        """Executes deep reasoning inference."""
        pass

    @abstractmethod
    async def code(self, prompt: str, **kwargs: Any) -> RuntimeResponse:
        """Executes code generation inference."""
        pass

    @abstractmethod
    async def vision(self, image_bytes_or_path: Any, prompt: str = "", **kwargs: Any) -> RuntimeResponse:
        """Executes multimodal visual reasoning."""
        pass

    @abstractmethod
    async def transcribe(self, audio_bytes_or_path: Any) -> RuntimeResponse:
        """Executes speech-to-text transcription."""
        pass

    @abstractmethod
    async def speak(self, text: str) -> RuntimeResponse:
        """Executes text-to-speech synthesis."""
        pass

    @abstractmethod
    async def embed(self, texts: List[str]) -> RuntimeResponse:
        """Executes vector embeddings generation."""
        pass

    @abstractmethod
    async def ocr(self, image_bytes_or_path: Any) -> RuntimeResponse:
        """Executes document OCR text extraction."""
        pass

    @abstractmethod
    async def translate(self, text: str, target_lang: str = "en") -> RuntimeResponse:
        """Executes machine translation."""
        pass

    @abstractmethod
    async def load_runtime(self, model_id: str) -> bool:
        """Loads model into active runtime memory."""
        pass

    @abstractmethod
    async def runtime_status(self) -> RuntimeHealth:
        """Retrieves runtime health status."""
        pass

    @abstractmethod
    async def active_models(self) -> List[str]:
        """Lists active models."""
        pass


class ILocalModelRuntime(ABC):
    """Legacy interface contract for local model runtime."""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs: Any) -> Any:
        pass

