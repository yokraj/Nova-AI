"""Request and response models for Ollama API communication.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class OllamaChatMessage(BaseModel):
    """Chat message structure inside Ollama calls."""

    role: str
    content: str


class OllamaChatRequest(BaseModel):
    """Payload to post generation chat completions to Ollama."""

    model: str
    messages: List[OllamaChatMessage]
    stream: bool = False
    options: Optional[Dict[str, Any]] = None


class OllamaEmbeddingRequest(BaseModel):
    """Payload to post text embeddings queries to Ollama."""

    model: str
    prompt: str
