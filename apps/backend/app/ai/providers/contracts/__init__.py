"""Abstract base contracts for AI providers.
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, List

from app.ai.models import (
    AIModelInfo,
    ChatRequest,
    ChatResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    ProviderHealth,
    StreamingChunk,
)


class ILLMProvider(ABC):
    """Abstract interface contract for chat and text streaming providers."""

    @abstractmethod
    async def chat(self, request: ChatRequest, **kwargs: Any) -> ChatResponse:
        """Sends chat messages payload generating a complete model response.

        Args:
            request: ChatRequest parameters.
            **kwargs: Extra arguments.

        Returns:
            ChatResponse data model.
        """
        pass

    @abstractmethod
    async def stream_chat(
        self, request: ChatRequest, **kwargs: Any
    ) -> AsyncGenerator[StreamingChunk, None]:
        """Streams text response chunks from chat messages payload.

        Args:
            request: ChatRequest parameters.
            **kwargs: Extra arguments.

        Yields:
            StreamingChunk fragments.
        """
        yield StreamingChunk(content="")

    @abstractmethod
    async def health(self) -> ProviderHealth:
        """Checks diagnostics health state of provider connection.

        Returns:
            ProviderHealth details.
        """
        pass

    @abstractmethod
    async def available_models(self) -> List[AIModelInfo]:
        """Details supported models configurations parameters.

        Returns:
            List of AIModelInfo metadata.
        """
        pass


class IEmbeddingProvider(ABC):
    """Abstract interface contract for generating vector embeddings."""

    @abstractmethod
    async def embed_text(self, request: EmbeddingRequest, **kwargs: Any) -> EmbeddingResponse:
        """Generates embedding vectors for text inputs.

        Args:
            request: EmbeddingRequest parameters.
            **kwargs: Extra arguments.

        Returns:
            EmbeddingResponse vector mappings.
        """
        pass

    @abstractmethod
    async def embed_batch(self, request: EmbeddingRequest, **kwargs: Any) -> EmbeddingResponse:
        """Generates embedding vectors for a batch of text inputs.

        Args:
            request: EmbeddingRequest parameters.
            **kwargs: Extra arguments.

        Returns:
            EmbeddingResponse vector mappings.
        """
        pass


class IImageProvider(ABC):
    """Abstract interface contract for text-to-image and image manipulation."""

    @abstractmethod
    async def generate_image(self, prompt: str, model: str, **kwargs: Any) -> str:
        """Generates image assets based on text instructions.

        Args:
            prompt: Visual description text.
            model: Model name.
            **kwargs: Extra arguments.

        Returns:
            Image url string or base64 data.
        """
        pass

    @abstractmethod
    async def edit_image(self, image_path: str, prompt: str, model: str, **kwargs: Any) -> str:
        """Modifies image content layout based on instructions.

        Args:
            image_path: Source file.
            prompt: Text adjustments edits prompt.
            model: Model name.
            **kwargs: Extra arguments.

        Returns:
            Modified image url.
        """
        pass


class ISpeechProvider(ABC):
    """Abstract interface contract for audio transcription and speech synthesis."""

    @abstractmethod
    async def speech_to_text(self, audio_data: bytes, model: str, **kwargs: Any) -> str:
        """Transcribes raw binary audio data into plain text.

        Args:
            audio_data: Audio file bytes.
            model: Model name.
            **kwargs: Extra arguments.

        Returns:
            Transcribed text description.
        """
        pass

    @abstractmethod
    async def text_to_speech(self, text: str, model: str, **kwargs: Any) -> bytes:
        """Synthesizes voice speech audio file bytes from text input.

        Args:
            text: Text to read.
            model: Model name.
            **kwargs: Extra arguments.

        Returns:
            Raw audio binary data.
        """
        pass


class IVisionProvider(ABC):
    """Abstract interface contract for vision and multimodal analysis."""

    @abstractmethod
    async def analyze_image(self, image_path: str, prompt: str, model: str, **kwargs: Any) -> str:
        """Extracts content context descriptions from visual files.

        Args:
            image_path: Source file.
            prompt: Specific question details.
            model: Model name.
            **kwargs: Extra arguments.

        Returns:
            Model response text.
        """
        pass
