"""Tests for the Enterprise Local RAG Memory System.
"""

import pytest
from app.ai.memory.embedding_manager import EmbeddingManager
from app.ai.memory.chunking_engine import DocumentChunker
from app.ai.memory.models import MemoryItem, MemoryType, DocumentChunk
from app.ai.memory.engine import LocalMemoryEngine
from app.ai.memory.configuration import MemoryConfiguration

@pytest.mark.anyio
async def test_memory_embedding_generation():
    """Verifies embedding generator yields correct dimension floats list."""
    mgr = EmbeddingManager()
    vector = await mgr.embed_text("hello world")
    assert isinstance(vector, list)
    assert len(vector) == 768
    assert all(isinstance(val, float) for val in vector)

@pytest.mark.anyio
async def test_document_chunking():
    """Verifies chunker splits large files into overlapping tokens."""
    chunker = DocumentChunker(chunk_size=100, chunk_overlap=10)
    parsed = {
        "source": "database.py",
        "content": "A" * 350,
        "metadata": {"author": "Nova"}
    }
    chunks = chunker.chunk_document(parsed)
    # 350 / 90 ~ 4 chunks
    assert len(chunks) >= 4
    assert chunks[0].content == "A" * 100
    assert chunks[0].metadata["author"] == "Nova"

@pytest.mark.anyio
async def test_vector_search_rag():
    """Verifies insert and query retrieval matches expected concepts."""
    # Force FAISS database selection for clean, offline-first local indexing tests
    config = MemoryConfiguration(
        vector_database="faiss",
        storage_path=".nova/test_memory/",
        similarity_threshold=0.0
    )
    engine = LocalMemoryEngine(config=config)
    
    await engine.store_memory(
        content="FastAPI authentication verifies usernames and passwords locally",
        memory_type=MemoryType.DOCUMENT,
        metadata={"source": "auth.py"}
    )
    
    # Query related concept
    context = await engine.retrieve_context("How login works?")
    assert "FastAPI authentication" in context.system_context

@pytest.mark.anyio
async def test_conversation_memory():
    """Verifies storing messages to conversation memory and fetching them back."""
    config = MemoryConfiguration(
        vector_database="faiss",
        storage_path=".nova/test_memory/",
        similarity_threshold=0.0
    )
    engine = LocalMemoryEngine(config=config)

    await engine.conversation.store_message(
        conversation_id="session-123",
        role="user",
        content="User prefers FastAPI with PostgreSQL database"
    )

    context = await engine.retrieve_context("FastAPI preferences")
    assert "User prefers FastAPI" in context.memory_context

@pytest.mark.anyio
async def test_project_memory():
    """Verifies storing architecture decision records to project memory."""
    config = MemoryConfiguration(
        vector_database="faiss",
        storage_path=".nova/test_memory/",
        similarity_threshold=0.0
    )
    engine = LocalMemoryEngine(config=config)

    await engine.project.record_technology_choice(
        title="Database selection",
        choice_description="Nova backend is built on SQLAlchemy and PostgreSQL"
    )

    context = await engine.retrieve_context("database tech choice")
    assert "SQLAlchemy and PostgreSQL" in context.project_context
