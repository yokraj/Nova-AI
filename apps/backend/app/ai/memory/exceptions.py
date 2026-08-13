"""Custom exceptions for the Enterprise Local RAG Memory System.
"""

from app.ai.exceptions import AiGatewayException

class MemoryError(AiGatewayException):
    """Base exception for all memory operations."""
    pass

class EmbeddingError(MemoryError):
    """Raised when generating embeddings fails."""
    pass

class VectorStoreError(MemoryError):
    """Raised when vector database operations fail."""
    pass

class RetrievalError(MemoryError):
    """Raised when memory retrieval fails."""
    pass

class DocumentProcessingError(MemoryError):
    """Raised when loading or parsing files fails."""
    pass

class MemoryLimitExceededError(MemoryError):
    """Raised when memory capacity limits are exceeded."""
    pass
