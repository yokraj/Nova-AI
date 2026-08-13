"""Domain models and schemas for the Enterprise Local RAG Memory System.
"""

from enum import Enum
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class MemoryType(str, Enum):
    """Classification types for memory segments."""
    CONVERSATION = "CONVERSATION"
    PROJECT = "PROJECT"
    CODE = "CODE"
    DOCUMENT = "DOCUMENT"
    KNOWLEDGE = "KNOWLEDGE"
    SYSTEM = "SYSTEM"

class MemoryItem(BaseModel):
    """Represents a unified memory node in the database."""
    id: UUID = Field(default_factory=uuid4)
    content: str
    memory_type: MemoryType
    metadata: Dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[List[float]] = Field(None, description="Optional vector float representation.")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    importance_score: float = Field(0.5, description="Value rating from 0.0 to 1.0.")

class DocumentChunk(BaseModel):
    """Represents a parsed partition of a larger document."""
    document_id: str
    chunk_index: int
    content: str
    tokens: int
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RetrievalResult(BaseModel):
    """Result payload mapping search matches."""
    memory_id: UUID
    content: str
    similarity_score: float
    source: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ContextPackage(BaseModel):
    """Bundled retrieval summaries formatted for prompt injections."""
    system_context: str = Field("")
    memory_context: str = Field("")
    project_context: str = Field("")
    code_context: str = Field("")
