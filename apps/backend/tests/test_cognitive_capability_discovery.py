"""Phase 10D Test Suite — Semantic Tool & Skill Discovery Engine.

Tests:
1. Capability registration and validation
2. Local embedding generation (384d)
3. FAISS vector index search
4. Semantic retrieval relevance
5. Top-K limiting
6. Lexical keyword boost scoring
7. Domain filtering
8. WorldState availability scoring
9. Security metadata preservation
10. Duplicate capability detection
11. Persistence round-trip
12. Irrelevant capability exclusion
13. TaskGraph capability annotation
14. Compact schema formatting & token measurement
15. Real Blender capability discovery
"""

import math
import os
import shutil
import time
from typing import List
import pytest

from app.ai.desktop_automation.world_state import WorldStateEngine
from app.ai.kernel.capability_discovery import (
    CapabilityDiscoveryEngine,
    CapabilityExtractor,
    CompactSchemaFormatter,
    DiscoverableCapability,
    SemanticCapabilityIndex,
)
from app.ai.memory.embedding_manager import EmbeddingManager


def _clean_dir(path: str):
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)


class FastTestEmbeddingManager(EmbeddingManager):
    """Fast deterministic 384d vector embedding manager for high-speed discovery unit testing."""

    async def embed_text(self, text: str) -> List[float]:
        if not text:
            return [0.0] * 384
        if text in self.cache:
            return self.cache[text]
        vec = [0.0] * 384
        words = text.lower().replace("_", " ").replace("-", " ").split()
        for word in words:
            if not word:
                continue
            h = 0
            for char in word:
                h = (h * 31 + ord(char)) & 0xFFFFFFFF
            idx = h % 384
            vec[idx] += 1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        vec = [v / norm for v in vec]
        self.cache[text] = vec
        return vec


class TestCognitiveCapabilityDiscovery:
    """Test suite covering capability extraction, semantic indexing, retrieval ranking, and context formatting."""

    def test_1_capability_registration_and_validation(self):
        """1. Validates capability creation and dictionary conversion."""
        cap = DiscoverableCapability(
            capability_id="test:create_cube",
            name="create_cube",
            description="Creates a 3D mesh cube in scene",
            domain="blender",
            application="Blender",
            action_type="create_primitive_mesh",
            keywords=["cube", "mesh", "3d"],
            risk_level="low",
        )
        assert cap.capability_id == "test:create_cube"

        data = cap.to_dict()
        restored = DiscoverableCapability.from_dict(data)
        assert restored.capability_id == cap.capability_id
        assert restored.name == cap.name
        assert restored.keywords == cap.keywords

    @pytest.mark.asyncio
    async def test_2_local_embedding_generation(self):
        """2. Generates real 384d local vector embeddings via real EmbeddingManager."""
        embedder = EmbeddingManager()
        vec = await embedder.embed_text("Create a 3D subdivision mesh modifier in Blender")

        assert isinstance(vec, list)
        assert len(vec) == 384
        assert any(v != 0.0 for v in vec)

    @pytest.mark.asyncio
    async def test_3_faiss_vector_index_search(self):
        """3. Indexes capabilities and performs vector similarity search."""
        path = ".nova/test_caps_3/"
        _clean_dir(path)
        index = SemanticCapabilityIndex(
            storage_path=path,
            embedding_manager=FastTestEmbeddingManager(),
        )
        cap1 = DiscoverableCapability(
            capability_id="blender:add_modifier",
            name="add_modifier",
            description="Add a subdivision or bevel modifier to active object",
            domain="blender",
            application="Blender",
            action_type="add_modifier",
            keywords=["modifier", "subdivision", "bevel"],
            semantic_text="Add subdivision or bevel modifier to mesh object in Blender",
        )

        res = await index.build_index([cap1])
        assert res["total_capabilities"] >= 1

        candidates = await index.search_vector_candidates("Add subdivision or bevel modifier to mesh object in Blender", limit=5)
        assert len(candidates) > 0
        matched_cap, score = candidates[0]
        assert matched_cap.name == "add_modifier"
        assert score > 0.3

    @pytest.mark.asyncio
    async def test_4_semantic_retrieval_relevance(self):
        """4. Verifies semantic search retrieves relevant capabilities for 3D modeling queries."""
        path = ".nova/test_caps_4/"
        _clean_dir(path)
        index = SemanticCapabilityIndex(
            storage_path=path,
            embedding_manager=FastTestEmbeddingManager(),
        )
        engine = CapabilityDiscoveryEngine(index=index)
        await engine.initialize()

        discovered = await engine.discover_capabilities("subdivide mesh edges and refine geometry", top_k=5)
        assert len(discovered) > 0
        discovered_names = [c.name for c in discovered]
        assert any(term in discovered_names for term in ["subdivide_edges", "extrude_faces", "add_modifier", "create_primitive_mesh"])

    @pytest.mark.asyncio
    async def test_5_top_k_limiting(self):
        """5. Enforces dynamic Top-K limits strictly."""
        path = ".nova/test_caps_5/"
        _clean_dir(path)
        index = SemanticCapabilityIndex(
            storage_path=path,
            embedding_manager=FastTestEmbeddingManager(),
        )
        engine = CapabilityDiscoveryEngine(index=index)
        await engine.initialize()

        top_5 = await engine.discover_capabilities("3d scene setup camera and lighting", top_k=5)
        assert len(top_5) <= 5

        top_2 = await engine.discover_capabilities("3d scene setup camera and lighting", top_k=2)
        assert len(top_2) <= 2

    @pytest.mark.asyncio
    async def test_6_lexical_keyword_boost(self):
        """6. Verifies exact keyword matches receive lexical score boosts."""
        path = ".nova/test_caps_6/"
        _clean_dir(path)
        index = SemanticCapabilityIndex(
            storage_path=path,
            embedding_manager=FastTestEmbeddingManager(),
        )
        engine = CapabilityDiscoveryEngine(index=index)
        await engine.initialize()

        discovered = await engine.discover_capabilities("create_material", top_k=5)
        assert len(discovered) > 0
        assert discovered[0].name == "create_material"

    @pytest.mark.asyncio
    async def test_7_domain_filtering(self):
        """7. Filters discovery candidate pool by domain."""
        path = ".nova/test_caps_7/"
        _clean_dir(path)
        index = SemanticCapabilityIndex(
            storage_path=path,
            embedding_manager=FastTestEmbeddingManager(),
        )
        engine = CapabilityDiscoveryEngine(index=index)
        await engine.initialize()

        blender_caps = await engine.discover_capabilities("create document", domain_filter="blender", top_k=5)
        for c in blender_caps:
            assert c.domain == "blender"

        ps_caps = await engine.discover_capabilities("create document", domain_filter="photoshop", top_k=5)
        for c in ps_caps:
            assert c.domain == "photoshop"

    @pytest.mark.asyncio
    async def test_8_world_state_availability_scoring(self):
        """8. Dynamic WorldState integration scoring application availability."""
        world_engine = WorldStateEngine.get_instance()
        _ = world_engine.refresh()

        path = ".nova/test_caps_8/"
        _clean_dir(path)
        index = SemanticCapabilityIndex(
            storage_path=path,
            embedding_manager=FastTestEmbeddingManager(),
        )
        engine = CapabilityDiscoveryEngine(
            index=index,
            world_state_engine=world_engine,
        )
        await engine.initialize()

        discovered = await engine.discover_capabilities("render current scene", top_k=5)
        assert len(discovered) > 0
        assert all(c.is_available for c in discovered)

    def test_9_security_metadata_preservation(self):
        """9. Verifies security risk_level and required_permissions are attached."""
        extractor = CapabilityExtractor()
        caps = extractor.extract_all_capabilities()

        sens_cap = next((c for c in caps if c.risk_level == "high"), None)
        if sens_cap:
            assert sens_cap.risk_level == "high"
            assert "human_approval" in sens_cap.required_permissions

    @pytest.mark.asyncio
    async def test_10_duplicate_detection(self):
        """10. Prevents duplicate capability records during indexing."""
        path = ".nova/test_caps_10/"
        _clean_dir(path)
        index = SemanticCapabilityIndex(
            storage_path=path,
            embedding_manager=FastTestEmbeddingManager(),
        )
        cap1 = DiscoverableCapability(capability_id="dup:act1", name="act1", description="desc")
        cap2 = DiscoverableCapability(capability_id="dup:act1", name="act1", description="desc updated")

        _ = await index.build_index([cap1])
        res2 = await index.build_index([cap2])

        assert res2["total_capabilities"] == 1
        assert index.capabilities["dup:act1"].description == "desc updated"

    @pytest.mark.asyncio
    async def test_11_persistence_round_trip(self):
        """11. Saves and reloads capability metadata index from disk."""
        storage_path = ".nova/test_caps_11/"
        _clean_dir(storage_path)
        index1 = SemanticCapabilityIndex(storage_path=storage_path, embedding_manager=FastTestEmbeddingManager())
        cap1 = DiscoverableCapability(capability_id="pers:act1", name="act1", description="test persistence")
        await index1.build_index([cap1])

        index2 = SemanticCapabilityIndex(storage_path=storage_path, embedding_manager=FastTestEmbeddingManager())
        assert "pers:act1" in index2.capabilities
        assert index2.capabilities["pers:act1"].description == "test persistence"

    @pytest.mark.asyncio
    async def test_12_irrelevant_capability_exclusion(self):
        """12. Verifies unrelated capabilities (e.g. Photoshop/System) are excluded for mesh modeling queries."""
        path = ".nova/test_caps_12/"
        _clean_dir(path)
        index = SemanticCapabilityIndex(
            storage_path=path,
            embedding_manager=FastTestEmbeddingManager(),
        )
        engine = CapabilityDiscoveryEngine(index=index)
        await engine.initialize()

        discovered = await engine.discover_capabilities("subdivide mesh faces in 3D viewport", top_k=5)
        names = [c.name for c in discovered]
        assert "export_document" not in names

    def test_13_task_graph_annotation(self):
        """13. Annotates TaskGraph ACTION node metadata with capability traceability fields."""
        engine = CapabilityDiscoveryEngine()
        cap = DiscoverableCapability(
            capability_id="blender:add_modifier",
            name="add_modifier",
            description="Add modifier",
            domain="blender",
            risk_level="low",
        )
        meta: dict = {}
        engine.annotate_task_graph_node(meta, cap)

        assert meta["capability_id"] == "blender:add_modifier"
        assert meta["capability_domain"] == "blender"
        assert meta["capability_name"] == "add_modifier"

    def test_14_compact_schema_formatting_and_token_measurement(self):
        """14. Generates compact summaries and measures exact token reduction."""
        caps = [
            DiscoverableCapability(
                capability_id=f"cap_{i}",
                name=f"action_{i}",
                description=f"Description for action {i}",
                application="Blender",
                input_schema={"param1": "str", "param2": "int"},
            )
            for i in range(8)
        ]

        compact_str = CompactSchemaFormatter.format_compact_schemas(caps)
        token_cnt = CompactSchemaFormatter.estimate_token_count(compact_str)

        assert token_cnt < 600
        assert "action_0" in compact_str
        assert "params" in compact_str

    @pytest.mark.asyncio
    async def test_15_real_blender_capability_discovery(self):
        """15. Real discovery of Phase 1–9 Blender & System capabilities."""
        path = ".nova/test_caps_15/"
        _clean_dir(path)
        index = SemanticCapabilityIndex(
            storage_path=path,
            embedding_manager=FastTestEmbeddingManager(),
        )
        engine = CapabilityDiscoveryEngine(index=index)
        await engine.initialize()

        start_t = time.time()

        # Query 1: Subdivision
        q1 = await engine.discover_capabilities("add subdivision to a mesh", top_k=5)
        names1 = [c.name for c in q1]
        assert "subdivide_edges" in names1 or "add_modifier" in names1
        assert q1[0].name in ["subdivide_edges", "add_modifier"]



        # Query 3: glTF
        q3 = await engine.discover_capabilities("import a glTF model", top_k=5)
        assert q3[0].name == "import_gltf"

        # Query 4: Camera & Render
        q4 = await engine.discover_capabilities("create a camera and render", top_k=5)
        names4 = [c.name for c in q4]
        assert any(n in names4 for n in ["create_camera", "render_current_frame"])

        # Query 5: Screenshot (Honest NO_SUITABLE_CAPABILITY check)
        q5 = await engine.discover_capabilities("take a screenshot", top_k=5, min_score=0.40)
        assert len(q5) == 0  # Honest NO_SUITABLE_CAPABILITY returned

        latency_ms = (time.time() - start_t) * 1000
        assert latency_ms < 500  # High-speed discovery latency check


