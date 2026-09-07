"""Tests for the Enterprise Local RAG Memory System with real neural embeddings.
"""

import os
import pytest
from app.ai.memory.embedding_manager import EmbeddingManager
from app.ai.memory.chunking_engine import DocumentChunker
from app.ai.memory.models import MemoryItem, MemoryType, DocumentChunk
from app.ai.memory.engine import LocalMemoryEngine
from app.ai.memory.configuration import MemoryConfiguration
from app.ai.memory.exceptions import EmbeddingError


@pytest.mark.anyio
async def test_memory_embedding_generation():
    """Verifies embedding generator yields correct dimension floats list."""
    mgr = EmbeddingManager()
    vector = await mgr.embed_text("hello world")
    assert isinstance(vector, list)
    assert len(vector) == 384 or len(vector) == 768
    assert all(isinstance(val, float) for val in vector)


@pytest.mark.anyio
async def test_document_chunking():
    """Verifies chunker splits large files into overlapping tokens."""
    chunker = DocumentChunker(chunk_size=100, chunk_overlap=10)
    parsed = {
        "source": "database.py",
        "content": "A" * 350,
        "metadata": {"author": "Nova"},
    }
    chunks = chunker.chunk_document(parsed)
    assert len(chunks) >= 4
    assert chunks[0].content == "A" * 100
    assert chunks[0].metadata["author"] == "Nova"


@pytest.mark.anyio
async def test_real_offline_semantic_ranking(tmp_path):
    """PROVES real neural semantic embedding ranking.
    
    Stores documents with distinct meanings:
    - Blender cube creation
    - weather forecast
    - database backup
    
    Queries 'How do I make a cube in Blender?' and verifies Blender document ranks highest.
    """
    storage_dir = str(tmp_path / "semantic_rag_test")
    config = MemoryConfiguration(
        vector_database="faiss",
        storage_path=storage_dir,
        similarity_threshold=0.0,
    )
    engine = LocalMemoryEngine(config=config)

    # Store 3 semantically distinct documents
    await engine.store_memory("Blender cube creation", MemoryType.DOCUMENT, metadata={"source": "blender.md"})
    await engine.store_memory("weather forecast", MemoryType.DOCUMENT, metadata={"source": "weather.md"})
    await engine.store_memory("database backup", MemoryType.DOCUMENT, metadata={"source": "db.md"})

    # Query semantically related phrase
    context = await engine.retrieve_context("How do I make a cube in Blender?", limit=3)
    results = await engine.store.search(await engine.embedding_mgr.embed_text("How do I make a cube in Blender?"), limit=3, threshold=0.0)

    assert len(results) == 3
    # Top result MUST be Blender cube creation
    top_doc = results[0].content
    assert top_doc == "Blender cube creation"
    assert results[0].similarity_score > results[1].similarity_score
    assert results[0].similarity_score > results[2].similarity_score


@pytest.mark.anyio
async def test_empty_query_rejection():
    """Verifies empty queries raise explicit EmbeddingError without fake success."""
    mgr = EmbeddingManager()
    with pytest.raises(EmbeddingError, match="cannot be empty"):
        await mgr.embed_text("")

    with pytest.raises(EmbeddingError, match="cannot be empty"):
        await mgr.embed_text("   ")


@pytest.mark.anyio
async def test_model_unavailable_rejection():
    """Verifies explicit failure when embedding model/environment is unavailable."""
    mgr = EmbeddingManager(venv_python="C:\\invalid\\nonexistent\\python.exe")
    with pytest.raises(EmbeddingError, match="not found"):
        await mgr.embed_text("Test query")


@pytest.mark.anyio
async def test_vector_dimensional_consistency():
    """Verifies dimensional consistency across multiple embeddings."""
    mgr = EmbeddingManager()
    v1 = await mgr.embed_text("First sample phrase")
    v2 = await mgr.embed_text("Second sample phrase")
    assert len(v1) == len(v2)
    assert mgr.validate_dimensions(v1) is True
    assert mgr.validate_dimensions(v2) is True
