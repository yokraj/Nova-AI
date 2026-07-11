"""AI Providers Contracts.
"""

from app.ai.providers.contracts import (
    IEmbeddingProvider,
    IImageProvider,
    ILLMProvider,
    ISpeechProvider,
    IVisionProvider,
)

__all__ = [
    "ILLMProvider",
    "IEmbeddingProvider",
    "IImageProvider",
    "ISpeechProvider",
    "IVisionProvider",
]
