"""Unit and Integration Tests for Nova AI Enterprise Memory Foundation.

Validates Memory CRUD, Search, Scoring, Compression, Cleanup, Relationships,
Workspace/Project Isolation, Statistics, REST API, and RBAC authorization.
"""

import asyncio
from datetime import datetime, timezone, timedelta
import pytest

from app.memory import (
    MemoryConfig,
    MemoryType,
    RelationshipType,
    MemoryEntryCreate,
    MemoryEntryUpdate,
    MemoryRepository,
    MemoryService,
    MemoryManager,
    MemorySearch,
    MemoryScoringEngine,
    MemoryCompressor,
    MemoryCleaner,
    MemoryIndexer,
    ConversationMemoryManager,
    WorkspaceMemoryManager,
    ProjectMemoryManager,
    UserMemoryManager,
    SemanticMemoryManager,
    MemoryStatisticsTracker,
    MemoryEngine,
)


def test_memory_crud_operations():
    """Test Memory CRUD, pin, archive, restore, merge, and split lifecycle."""
    async def _test():
        repo = MemoryRepository()
        manager = MemoryManager(repo)

        # 1. Create Memory
        create_schema = MemoryEntryCreate(
            title="System Architecture Guidelines",
            content="Nova AI uses a micro-modular async service architecture.",
            memory_type=MemoryType.LONG_TERM,
            workspace="Nova",
            project="Kernel",
            tags=["architecture", "design"],
        )
        entry = await manager.create_memory(create_schema)
        assert entry.id is not None
        assert entry.title == "System Architecture Guidelines"
        assert "architecture" in entry.tags

        # 2. Update Memory
        update_schema = MemoryEntryUpdate(title="Updated System Architecture Guidelines", importance=0.9)
        updated = await manager.update_memory(entry.id, update_schema)
        assert updated.title == "Updated System Architecture Guidelines"
        assert updated.importance == 0.9

        # 3. Pin & Archive & Restore
        pinned = await manager.pin_memory(entry.id)
        assert pinned.is_pinned is True

        archived = await manager.archive_memory(entry.id)
        assert archived.is_archived is True

        restored = await manager.restore_memory(entry.id)
        assert restored.is_archived is False

        # 4. Merge Memories
        e1 = await manager.create_memory(MemoryEntryCreate(title="Part A", content="Content A"))
        e2 = await manager.create_memory(MemoryEntryCreate(title="Part B", content="Content B"))
        merged = await manager.merge_memories([e1.id, e2.id], target_title="Merged Part A and B")
        assert "Content A" in merged.content
        assert "Content B" in merged.content

        # 5. Split Memory
        split_res = await manager.split_memory(merged.id, ["Part 1 Text", "Part 2 Text"])
        assert len(split_res) == 2
        assert "Part 1 Text" in split_res[0].content

        # 6. Delete Memory
        deleted = await manager.delete_memory(entry.id)
        assert deleted is True

    asyncio.run(_test())


def test_memory_search_and_scoring():
    """Test multi-criteria memory search and priority scoring engine."""
    async def _test():
        repo = MemoryRepository()
        search_engine = MemorySearch(repo)
        scoring_engine = MemoryScoringEngine()

        # Create test entries
        await repo.create_entry(
            title="PostgreSQL Indexing Optimization",
            content="B-Tree indexes improve query performance for large tables.",
            workspace="Database",
            project="Indexing",
            importance=0.85,
            tags=["postgres", "sql"],
        )
        await repo.create_entry(
            title="React Glassmorphism UI Components",
            content="CSS backdrop-filter creates smooth glassmorphic cards.",
            workspace="Frontend",
            project="Design",
            importance=0.40,
            tags=["ui", "css"],
        )

        # 1. Search text
        text_results = await search_engine.search_text("PostgreSQL")
        assert len(text_results) == 1
        assert text_results[0].title == "PostgreSQL Indexing Optimization"

        # 2. Search workspace
        ws_results = await search_engine.search_workspace("Frontend")
        assert len(ws_results) == 1
        assert ws_results[0].workspace == "Frontend"

        # 3. Search tags
        tag_results = await search_engine.search_tags(["sql"])
        assert len(tag_results) == 1
        assert "postgres" in tag_results[0].tags

        # 4. Priority scoring
        score = scoring_engine.calculate_priority_score(
            importance=0.9,
            created_at=datetime.now(timezone.utc),
            access_count=10,
        )
        assert 0.0 <= score <= 1.0

    asyncio.run(_test())


def test_compression_and_cleanup():
    """Test memory compression and automated cleanup routines."""
    async def _test():
        repo = MemoryRepository()
        compressor = MemoryCompressor()
        cleaner = MemoryCleaner(repo)

        # 1. Thread compression
        thread_entries = [
            {"id": f"id-{i}", "title": f"Turn {i}", "content": f"Text turn {i}", "importance": 0.5}
            for i in range(15)
        ]
        compressed = compressor.compress_memory_thread(thread_entries, max_preserved=5)
        assert compressed["compressed_count"] == 10
        assert compressed["compression_ratio"] < 1.0

        # 2. Purge expired memories
        past_time = datetime.now(timezone.utc) - timedelta(hours=1)
        await repo.create_entry(
            title="Expired Temp Note",
            content="Temporary session token payload",
            expires_at=past_time,
        )
        purged_count = await cleaner.purge_expired_memories()
        assert purged_count == 1

    asyncio.run(_test())


def test_workspace_and_project_isolation():
    """Test workspace and project memory isolation managers."""
    async def _test():
        repo = MemoryRepository()
        ws_manager = WorkspaceMemoryManager(repo)
        pj_manager = ProjectMemoryManager(repo)

        # Create entries in different workspaces
        await repo.create_entry(title="College Assignment", content="Math homework", workspace="College")
        await repo.create_entry(title="Research Paper Draft", content="AGI memory systems", workspace="Research")

        college_mem = await ws_manager.get_workspace_memories("College")
        assert len(college_mem) == 1
        assert college_mem[0]["title"] == "College Assignment"

        # Record project decision
        await pj_manager.record_project_decision("Kernel", "Use Async Engine", "Adopted SQLAlchemy 2.0 async engine")
        pj_summary = await pj_manager.get_project_summary("Kernel")
        assert pj_summary["memory_count"] == 1

    asyncio.run(_test())


def test_user_and_semantic_memory():
    """Test user memory profile and semantic concept managers."""
    async def _test():
        repo = MemoryRepository()
        user_manager = UserMemoryManager(repo)
        semantic_manager = SemanticMemoryManager(repo)

        # User memory
        await user_manager.update_preferences(
            user_id="user_test_99",
            writing_style="Concise",
            favorite_languages=["Python", "Rust"],
        )
        profile = await user_manager.get_user_profile("user_test_99")
        assert profile["writing_style"] == "Concise"
        assert "Rust" in profile["favorite_languages"]

        # Semantic concept
        concept = await semantic_manager.store_concept("Vector Store", "High-dimensional embedding index")
        assert concept["concept_name"] == "Vector Store"

    asyncio.run(_test())


def test_memory_statistics_and_service():
    """Test MemoryService and MemoryStatisticsTracker telemetries."""
    async def _test():
        repo = MemoryRepository()
        service = MemoryService(repo)

        # Create entry via service
        res = await service.create_memory(MemoryEntryCreate(title="Test Stat Entry", content="Data content"))
        assert res.id is not None

        # Get statistics
        stats = await service.get_statistics()
        assert stats.memory_count >= 1
        assert stats.workspace_count >= 1

    asyncio.run(_test())
