"""Embedding Models Provider Abstraction Module.

Defines local neural embedding provider interfaces powered by local Ollama (nomic-embed-text, all-minilm, bge),
with strict dimension validation, zero cloud dependencies, and transparent error reporting when local models are unavailable.
"""

import hashlib
import math
from typing import Any, Dict, List, Optional
import httpx
import structlog

from app.vector_memory.config import VectorConfig
from app.vector_memory.exceptions import (
    EmbeddingGenerationError,
    EmbeddingModelUnavailableError,
    VectorDimensionMismatchError,
)

logger = structlog.get_logger(__name__)


class BaseEmbeddingProvider:
    """Abstract base class for embedding model providers."""

    def __init__(self, model_name: str, dimension: int, is_neural: bool = True) -> None:
        self.model_name = model_name
        self.dimension = dimension
        self.is_neural = is_neural

    async def generate_vector(self, text: str) -> List[float]:
        """Generates embedding vector for a single text input."""
        raise NotImplementedError

    async def check_availability(self) -> Dict[str, Any]:
        """Checks whether the underlying model is available at runtime."""
        return {"available": True, "model": self.model_name, "is_neural": self.is_neural}


class OllamaNeuralEmbeddingProvider(BaseEmbeddingProvider):
    """Local neural embedding provider integrating genuine local models via Ollama."""

    def __init__(
        self,
        model_name: str = "nomic-embed-text",
        dimension: int = 768,
        base_url: str = "http://127.0.0.1:11434",
        timeout_seconds: float = 30.0,
    ) -> None:
        super().__init__(model_name=model_name, dimension=dimension, is_neural=True)
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        logger.info(
            "ollama_neural_embedding_provider_initialized",
            model_name=self.model_name,
            dimension=self.dimension,
            base_url=self.base_url,
        )

    async def generate_vector(self, text: str) -> List[float]:
        """Generates a genuine neural embedding vector via local Ollama API."""
        if not text or not text.strip():
            raise EmbeddingGenerationError("Cannot generate embedding for empty text input.")

        clean_text = text.strip()

        # 1. Attempt Modern Ollama /api/embed Endpoint
        embed_url = f"{self.base_url}/api/embed"
        legacy_url = f"{self.base_url}/api/embeddings"
        payload_modern = {"model": self.model_name, "input": clean_text}
        payload_legacy = {"model": self.model_name, "prompt": clean_text}

        raw_vector: Optional[List[float]] = None

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                # Try /api/embed first
                response = await client.post(embed_url, json=payload_modern)

                if response.status_code == 200:
                    data = response.json()
                    embeddings = data.get("embeddings", [])
                    if embeddings and isinstance(embeddings, list) and len(embeddings) > 0:
                        raw_vector = embeddings[0]
                elif response.status_code == 404:
                    # Fallback to legacy /api/embeddings endpoint
                    logger.debug("ollama_embed_endpoint_not_found_falling_back_to_embeddings", model=self.model_name)
                    legacy_resp = await client.post(legacy_url, json=payload_legacy)
                    if legacy_resp.status_code == 200:
                        data = legacy_resp.json()
                        raw_vector = data.get("embedding")
                    else:
                        self._handle_ollama_error(legacy_resp)
                else:
                    self._handle_ollama_error(response)

        except httpx.ConnectError as ce:
            logger.error("ollama_connection_refused", error=str(ce), base_url=self.base_url)
            raise EmbeddingModelUnavailableError(
                f"Cannot connect to local Ollama service at '{self.base_url}'. "
                f"Please verify that Ollama is running and accessible on port 11434.",
                details={"base_url": self.base_url, "error": str(ce)},
            ) from ce
        except httpx.TimeoutException as te:
            logger.error("ollama_embedding_timeout", model=self.model_name, timeout=self.timeout_seconds)
            raise EmbeddingGenerationError(
                f"Timeout waiting for Ollama embedding generation after {self.timeout_seconds}s for model '{self.model_name}'.",
                details={"model": self.model_name, "timeout": self.timeout_seconds},
            ) from te
        except (EmbeddingGenerationError, EmbeddingModelUnavailableError, VectorDimensionMismatchError):
            raise
        except Exception as exc:
            logger.error("ollama_embedding_unexpected_failure", error=str(exc))
            raise EmbeddingGenerationError(
                f"Failed to generate neural embedding via Ollama: {exc}",
                details={"model": self.model_name, "error": str(exc)},
            ) from exc

        if not raw_vector or not isinstance(raw_vector, list):
            raise EmbeddingGenerationError(
                f"Ollama returned malformed or empty embedding vector for model '{self.model_name}'.",
                details={"model": self.model_name},
            )

        # 2. Dimension Validation
        actual_dim = len(raw_vector)
        if actual_dim != self.dimension:
            raise VectorDimensionMismatchError(
                f"Returned neural vector dimension ({actual_dim}) does not match expected dimension ({self.dimension}) "
                f"for model '{self.model_name}'.",
                details={"expected": self.dimension, "actual": actual_dim, "model": self.model_name},
            )

        # 3. L2 Normalization
        magnitude = math.sqrt(sum(v * v for v in raw_vector))
        if magnitude == 0.0:
            return raw_vector

        normalized = [round(v / magnitude, 6) for v in raw_vector]
        return normalized

    def _handle_ollama_error(self, response: httpx.Response) -> None:
        """Parses error payload from Ollama and raises appropriate typed exception."""
        error_msg = f"HTTP {response.status_code}"
        try:
            err_json = response.json()
            error_msg = err_json.get("error", str(err_json))
        except Exception:
            error_msg = response.text or error_msg

        logger.error("ollama_embedding_api_error", status_code=response.status_code, error=error_msg, model=self.model_name)

        if "does not support embeddings" in error_msg.lower():
            raise EmbeddingModelUnavailableError(
                f"Local Ollama server does not have embeddings enabled: '{error_msg}'. "
                f"Please start Ollama with the `--embeddings` flag to enable neural vector embeddings.",
                details={"status_code": response.status_code, "error": error_msg, "model": self.model_name},
            )

        if "not found" in error_msg.lower() or "pull" in error_msg.lower() or response.status_code == 404:
            raise EmbeddingModelUnavailableError(
                f"Local neural embedding model '{self.model_name}' is not installed in Ollama: '{error_msg}'. "
                f"Please run 'ollama pull {self.model_name}' to download and activate this model.",
                details={"status_code": response.status_code, "error": error_msg, "model": self.model_name},
            )

        raise EmbeddingGenerationError(
            f"Ollama embedding API error ({response.status_code}): {error_msg}",
            details={"status_code": response.status_code, "error": error_msg, "model": self.model_name},
        )

    async def check_availability(self) -> Dict[str, Any]:
        """Queries local Ollama inventory to verify if model is installed."""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    models = [m.get("name", "") for m in res.json().get("models", [])]
                    clean_name = self.model_name.split(":")[0]
                    matched = any(clean_name in m for m in models)
                    return {
                        "available": matched,
                        "model": self.model_name,
                        "installed_models": models,
                        "is_neural": True,
                        "dimension": self.dimension,
                    }
        except Exception as exc:
            return {
                "available": False,
                "model": self.model_name,
                "error": str(exc),
                "is_neural": True,
                "dimension": self.dimension,
            }
        return {"available": False, "model": self.model_name, "is_neural": True, "dimension": self.dimension}


class DeterministicLocalEmbeddingProvider(BaseEmbeddingProvider):
    """Legacy deterministic pseudo-embedding provider (DEPRECATED).
    
    WARNING: Generates SHA-256 hash-derived float vectors. These are strictly non-semantic
    and retained only for backward-compatible test fixtures. Never used as silent fallback for neural requests.
    """

    def __init__(self, model_name: str = "legacy-hash-fallback", dimension: int = 384) -> None:
        super().__init__(model_name=model_name, dimension=dimension, is_neural=False)
        logger.warning("deprecated_pseudo_embedding_provider_initialized", model=model_name)

    async def generate_vector(self, text: str) -> List[float]:
        """Generates a non-semantic hash vector from text content (deprecated)."""
        if not text:
            raise EmbeddingGenerationError("Cannot generate embedding for empty text input.")

        seed_hash = hashlib.sha256(f"{self.model_name}:{text}".encode("utf-8")).hexdigest()
        raw_vector: List[float] = []
        for i in range(self.dimension):
            chunk = seed_hash[(i % len(seed_hash)):(i % len(seed_hash)) + 4]
            val = (int(chunk, 16) / 65535.0) - 0.5
            raw_vector.append(val)

        magnitude = math.sqrt(sum(v * v for v in raw_vector))
        if magnitude == 0.0:
            magnitude = 1.0

        return [round(v / magnitude, 6) for v in raw_vector]


class ModelRegistry:
    """Registry managing available local embedding model providers."""

    def __init__(self, config: Optional[VectorConfig] = None) -> None:
        self.config = config or VectorConfig()
        self._providers: Dict[str, BaseEmbeddingProvider] = {}
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        """Instantiates default supported local neural model providers."""
        base_url = getattr(self.config, "ollama_base_url", "http://127.0.0.1:11434")
        timeout = getattr(self.config, "ollama_timeout_seconds", 30.0)

        for model_name, dim in self.config.supported_models.items():
            canonical_name = self.normalize_model_name(model_name)
            self._providers[canonical_name] = OllamaNeuralEmbeddingProvider(
                model_name=canonical_name,
                dimension=dim,
                base_url=base_url,
                timeout_seconds=timeout,
            )
            # Retain original key mapping if different
            if model_name != canonical_name:
                self._providers[model_name] = self._providers[canonical_name]

        logger.info("embedding_models_registry_initialized", supported_count=len(self._providers), default_model=self.config.default_model)

    def normalize_model_name(self, model_name: str) -> str:
        """Normalizes model aliases and tags into canonical model names."""
        clean = model_name.strip()
        lower = clean.lower()

        if lower in ("nomic embed", "nomic-embed", "nomic-embed-text", "nomic_embed_text"):
            return "nomic-embed-text"
        if lower in ("all-minilm", "all-minilm-l6-v2", "sentence-transformers"):
            return "all-minilm"
        if lower in ("bge-small", "baai/bge-small-en-v1.5"):
            return "bge-small"
        if lower in ("bge-base", "baai/bge-base-en-v1.5"):
            return "bge-base"

        return clean

    def get_provider(self, model_name: str) -> BaseEmbeddingProvider:
        """Retrieves neural provider instance by model name with automatic dimension resolution."""
        canonical = self.normalize_model_name(model_name)
        if canonical in self._providers:
            return self._providers[canonical]
        if model_name in self._providers:
            return self._providers[model_name]

        # Resolve dimension dynamically from configuration or default
        dim = self.config.supported_models.get(canonical, self.config.supported_models.get(model_name, self.config.default_dimension))
        base_url = getattr(self.config, "ollama_base_url", "http://127.0.0.1:11434")
        timeout = getattr(self.config, "ollama_timeout_seconds", 30.0)

        provider = OllamaNeuralEmbeddingProvider(
            model_name=canonical,
            dimension=dim,
            base_url=base_url,
            timeout_seconds=timeout,
        )
        self._providers[canonical] = provider
        return provider
