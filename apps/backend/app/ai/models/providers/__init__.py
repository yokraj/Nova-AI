"""Model provider implementations for local and remote inference engines.
"""

from app.ai.models.providers.ollama_provider import OllamaProvider
from app.ai.models.providers.llamacpp_provider import LlamaCppProvider
from app.ai.models.providers.transformers_provider import TransformersProvider
from app.ai.models.providers.whisper_provider import WhisperProvider
from app.ai.models.providers.piper_provider import PiperProvider
from app.ai.models.providers.paddleocr_provider import PaddleOCRProvider
from app.ai.models.providers.embedding_provider import EmbeddingProvider
from app.ai.models.providers.openai_provider import OpenAIProvider
from app.ai.models.providers.gemini_provider import GeminiProvider
from app.ai.models.providers.anthropic_provider import AnthropicProvider

__all__ = [
    "OllamaProvider",
    "LlamaCppProvider",
    "TransformersProvider",
    "WhisperProvider",
    "PiperProvider",
    "PaddleOCRProvider",
    "EmbeddingProvider",
    "OpenAIProvider",
    "GeminiProvider",
    "AnthropicProvider",
]
