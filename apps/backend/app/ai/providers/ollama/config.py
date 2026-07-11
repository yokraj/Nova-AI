"""Configuration options for the Ollama provider.
"""

import os
from pydantic import BaseModel, Field


class OllamaConfig(BaseModel):
    """Configuration options for the Ollama provider."""

    host: str = Field(default_factory=lambda: os.getenv("OLLAMA_HOST", "http://localhost:11434"))
    timeout_seconds: float = Field(default_factory=lambda: float(os.getenv("OLLAMA_TIMEOUT", "30.0")))
    default_model: str = Field(default_factory=lambda: os.getenv("DEFAULT_MODEL", "llama3"))
