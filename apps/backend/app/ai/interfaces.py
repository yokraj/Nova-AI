"""AI Provider contracts and interfaces for Nova AI Gateway.

Establishes provider-independent contracts for LLMs, embeddings, image generation,
speech, and vision providers.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, AsyncGenerator, List
from pydantic import BaseModel, Field


class ProviderCapability(str, Enum):
    """Enumerate the capabilities supported by AI providers."""

    CHAT = "chat"
    EMBEDDINGS = "embeddings"
    IMAGE = "image"
    SPEECH = "speech"
    VISION = "vision"


class ProviderType(str, Enum):
    """Enumerate the types of AI providers supported by the gateway."""

    OPENAI = "openai"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    MOCK = "mock"


class AIModel(BaseModel):
    """Metadata detailing properties and cost limits of a specific AI model."""

    model_name: str = Field(..., description="Unique model identifier.")
    context_window: int = Field(..., description="Context window token size.")
    max_output_tokens: int = Field(..., description="Maximum allowed output tokens.")
    capabilities: List[ProviderCapability] = Field(..., description="Capabilities supported by the model.")
    cost_per_input_token: float = Field(0.0, description="Cost per million input tokens in USD.")
    cost_per_output_token: float = Field(0.0, description="Cost per million output tokens in USD.")


class ProviderHealth(BaseModel):
    """Snapshot indicating current provider latency and status."""

    is_healthy: bool = Field(True, description="True if online and responding.")
    latency_ms: float = Field(0.0, description="Latency sample duration in milliseconds.")
    status_code: int = Field(200, description="Diagnostic HTTP status code.")


class ILLMProvider(ABC):
    """Abstraction contract managing Large Language Model chat and health operations."""

    @abstractmethod
    async def chat(self, prompt: str, model: str, **kwargs: Any) -> str:
        """Sends a non-streaming chat prompt to the model.

        Args:
            prompt: Text content prompt.
            model: Target model name.
            **kwargs: Extra parameters.

        Returns:
            Text content response.
        """
        pass

    @abstractmethod
    async def stream_chat(self, prompt: str, model: str, **kwargs: Any) -> AsyncGenerator[str, None]:
        """Sends a streaming chat prompt yielding content chunks.

        Args:
            prompt: Text content prompt.
            model: Target model name.
            **kwargs: Extra parameters.

        Yields:
            Token chunks.
        """
        yield ""

    @abstractmethod
    async def health(self) -> ProviderHealth:
        """Returns the health diagnostics status of the provider.

        Returns:
            ProviderHealth snapshot model.
        """
        pass

    @abstractmethod
    async def available_models(self) -> List[AIModel]:
        """Returns a list of AIModel metadata objects supported by this provider.

        Returns:
            List of AIModel details.
        """
        pass


class IEmbeddingProvider(ABC):
    """Abstraction contract managing text embedding generators."""

    @abstractmethod
    async def embed_text(self, text: str, model: str, **kwargs: Any) -> List[float]:
        """Generates embedding vector for a single text block.

        Args:
            text: Input text string.
            model: Target embeddings model.
            **kwargs: Extra configurations.

        Returns:
            Vector array represented as a list of floats.
        """
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str], model: str, **kwargs: Any) -> List[List[float]]:
        """Generates embedding vectors for a batch of text blocks.

        Args:
            texts: List of input text strings.
            model: Target embeddings model.
            **kwargs: Extra configurations.

        Returns:
            List of vector arrays.
        """
        pass


class IImageProvider(ABC):
    """Abstraction contract managing image generation and manipulation."""

    @abstractmethod
    async def generate_image(self, prompt: str, model: str, **kwargs: Any) -> str:
        """Generates an image from a prompt text description.

        Args:
            prompt: Text description of the image to generate.
            model: Target image model.
            **kwargs: Extra configurations.

        Returns:
            Public image URL or base64 representation.
        """
        pass

    @abstractmethod
    async def edit_image(self, image_path: str, prompt: str, model: str, **kwargs: Any) -> str:
        """Edits an existing image based on a prompt instruction.

        Args:
            image_path: Location of the source image.
            prompt: Editing instructions.
            model: Target image model.
            **kwargs: Extra configurations.

        Returns:
            Public image URL or base64 representation of the edited image.
        """
        pass


class ISpeechProvider(ABC):
    """Abstraction contract managing speech-to-text and text-to-speech conversions."""

    @abstractmethod
    async def speech_to_text(self, audio_data: bytes, model: str, **kwargs: Any) -> str:
        """Transcribes audio binary data to text transcripts.

        Args:
            audio_data: Raw audio file bytes.
            model: Target transcription model.
            **kwargs: Extra configurations.

        Returns:
            Transcribed text.
        """
        pass

    @abstractmethod
    async def text_to_speech(self, text: str, model: str, **kwargs: Any) -> bytes:
        """Synthesizes text content into raw audio binary data.

        Args:
            text: Text to synthesize.
            model: Target TTS model.
            **kwargs: Extra configurations.

        Returns:
            Raw audio binary file bytes.
        """
        pass


class IVisionProvider(ABC):
    """Abstraction contract managing multimodal image analysis."""

    @abstractmethod
    async def analyze_image(self, image_path: str, prompt: str, model: str, **kwargs: Any) -> str:
        """Analyzes an image and returns a text summary or response.

        Args:
            image_path: Location of the source image.
            prompt: Analysis question or instruction.
            model: Target multimodal model.
            **kwargs: Extra configurations.

        Returns:
            Text analysis response.
        """
        pass
