"""Interface definitions for vector storage and embedding generation components.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID
from app.ai.memory.models import MemoryItem, RetrievalResult
from app.ai.memory.embedding_provider import IEmbeddingProvider
from app.ai.memory.vector_store import IVectorStore
