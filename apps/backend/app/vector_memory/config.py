"""Vector Memory Configuration Module.

Defines Pydantic settings for embedding models, vector dimensions, vector store backends,
distance metrics, cache capacities, and batch processing bounds.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class VectorConfig(BaseModel):
    """Configuration settings for Enterprise Vector Database & Embedding Engine."""

    # Default Embedding Engine Settings (Local-First Neural)
    default_provider: str = Field(default="ollama", description="Primary embedding provider")
    default_model: str = Field(default="nomic-embed-text", description="Primary local embedding model tag")
    default_dimension: int = Field(default=768, description="Embedding vector space dimensionality")
    distance_metric: str = Field(default="cosine", description="Primary vector distance metric (cosine, euclidean, dot)")
    ollama_base_url: str = Field(default="http://127.0.0.1:11434", description="Local Ollama instance URL")
    ollama_timeout_seconds: float = Field(default=30.0, description="Timeout for local embedding requests")

    # Vector Store Backend Configuration
    vector_store_backend: str = Field(default="sqlite", description="Active vector store backend (sqlite, chromadb, faiss, qdrant, milvus)")
    vector_store_path: str = Field(default="./data/vector_store", description="Local persistence directory path")

    # Cache & Optimization Limits
    cache_capacity: int = Field(default=5000, description="Max vector embedding cache capacity")
    cache_ttl_seconds: float = Field(default=3600.0, description="Cache entry TTL in seconds")
    batch_size: int = Field(default=64, description="Default batch embedding generation size")
    max_top_k: int = Field(default=100, description="Maximum vector retrieval candidate limit")

    # Supported Local Embedding Models Registry
    supported_models: Dict[str, int] = Field(
        default_factory=lambda: {
            "nomic-embed-text": 768,
            "all-minilm": 384,
            "bge-small": 384,
            "bge-base": 768,
            "BAAI/bge-small-en-v1.5": 384,
            "BAAI/bge-base-en-v1.5": 768,
            "Nomic Embed": 768,
            "E5 Small": 384,
            "E5 Base": 768,
            "Instructor": 768,
            "Sentence Transformers": 384,
        }
    )
