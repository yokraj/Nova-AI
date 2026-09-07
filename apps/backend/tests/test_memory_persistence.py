"""Focused Memory Persistence Tests.

Proves: write memory -> close/reinitialize memory layer -> read memory -> same memory is returned.
Uses SQLite database and persistent file stores for verification across process restarts.
"""

import os
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.database.base import Base
from app.memory.repository import MemoryRepository
from app.memory.models import MemoryEntryModel
from app.ai.agents.shared_memory import SharedAgentMemory
from app.ai.memory.faiss_store import FAISSVectorStore
from app.ai.memory.models import MemoryItem, MemoryType


@pytest.mark.anyio
async def test_sqlite_memory_repository_persistence(tmp_path):
    """Proves SQLite database memory repository write -> close -> reinitialize -> read persistence."""
    db_file = str(tmp_path / "test_persistence.db")
    db_url = f"sqlite+aiosqlite:///{db_file}"

    engine_1 = create_async_engine(db_url)
    async with engine_1.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker_1 = async_sessionmaker(engine_1, expire_on_commit=False, class_=AsyncSession)

    # 1. WRITE MEMORY
    async with session_maker_1() as session1:
        repo1 = MemoryRepository(session=session1)
        created = await repo1.create_entry(
            title="Database Architecture",
            content="Nova uses SQLite and PostgreSQL for canonical persistence",
            memory_type="long_term",
            workspace="Nova",
            tags=["database", "architecture"],
        )
        entry_id = created.id
        assert entry_id is not None

    # 2. CLOSE INITIAL ENGINE/SESSION
    await engine_1.dispose()

    # 3. REINITIALIZE MEMORY LAYER WITH NEW ENGINE ON SAME SQLITE DB FILE
    engine_2 = create_async_engine(db_url)
    session_maker_2 = async_sessionmaker(engine_2, expire_on_commit=False, class_=AsyncSession)

    # 4. READ MEMORY AND VERIFY IDENTICAL ITEM RETURNED
    async with session_maker_2() as session2:
        repo2 = MemoryRepository(session=session2)
        retrieved = await repo2.get_entry_by_id(entry_id)
        assert retrieved is not None

        assert retrieved.id == entry_id
        assert retrieved.title == "Database Architecture"
        assert "SQLite and PostgreSQL" in retrieved.content

    await engine_2.dispose()


@pytest.mark.anyio
async def test_shared_agent_memory_restart_persistence(tmp_path):
    """Proves SharedAgentMemory write -> close/reinitialize -> read persistence across process restarts."""
    storage_file = str(tmp_path / "shared_mem.json")

    # 1. WRITE MEMORY IN INITIAL INSTANCE
    mem1 = SharedAgentMemory(storage_path=storage_file)
    mem1.store("active_goal", "Implement F1.56A Unified Persistence", author="Orchestrator", category="goals")
    assert mem1.retrieve("active_goal") == "Implement F1.56A Unified Persistence"

    # 2. SIMULATE RESTART: INSTANTIATE NEW MEMORY OBJECT
    mem2 = SharedAgentMemory(storage_path=storage_file)
    restored = mem2.retrieve("active_goal")

    # 3. VERIFY SAME MEMORY RETURNED FROM DISK
    assert restored == "Implement F1.56A Unified Persistence"
    assert "active_goal" in mem2.list_keys()


@pytest.mark.anyio
async def test_faiss_vector_store_disk_persistence(tmp_path):
    """Proves FAISSVectorStore index write -> reinitialize -> search persistence."""
    store_dir = str(tmp_path / "vector_store")

    # 1. WRITE MEMORY ITEM
    store1 = FAISSVectorStore(storage_path=store_dir)
    item = MemoryItem(
        content="Persistent vector memory item",
        memory_type=MemoryType.DOCUMENT,
        metadata={"category": "doc"},
        embedding=[0.1] * 768,
    )
    await store1.add([item])
    item_id = item.id

    # 2. REINITIALIZE VECTOR STORE FROM DISK
    store2 = FAISSVectorStore(storage_path=store_dir)
    assert await store2.count() == 1

    results = await store2.search([0.1] * 768, limit=1, threshold=0.0)
    assert len(results) == 1
    assert results[0].memory_id == item_id
    assert results[0].content == "Persistent vector memory item"
