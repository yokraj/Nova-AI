"""Configuration schema for the Enterprise Local RAG Memory System.
"""

from pydantic import BaseModel, Field

class MemoryConfiguration(BaseModel):
    """Memory configuration settings for RAG, chunking, and local databases."""

    embedding_model: str = Field("nomic-embed-text", description="Default local embedding model tag.")
    vector_database: str = Field("pgvector", description="Target vector database provider (pgvector or faiss).")
    chunk_size: int = Field(500, description="Target chunk size in characters/tokens.")
    chunk_overlap: int = Field(50, description="Target chunk overlap size.")
    max_memory_items: int = Field(1000, description="Upper bound capacity limit.")
    similarity_threshold: float = Field(0.75, description="Filter cosine similarity threshold.")
    enable_compression: bool = Field(True, description="Enables context summaries compression.")
    storage_path: str = Field(".nova/memory/", description="Root storage directory for FAISS backups.")
