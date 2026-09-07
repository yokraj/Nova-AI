"""Focused Tests for Knowledge Graph + RAG Fusion (F1.56D).

Proves:
A. Persist graph (User -> works_on -> Nova -> uses -> Blender) -> Query retrieves real persisted graph context into AgentRuntime planning context.
B. Unrelated entities/relationships (Pizza -> cooked_in -> Oven) are filtered out.
C. Semantic memory and Knowledge Graph context coexist in the same ContextPackage.
D. Restart/reinitialize graph storage from disk -> relationships remain retrievable.
E. Forced graph retrieval failure -> graceful degradation, no fabricated relationships.
F. EXPLAIN, GUIDE, and EXECUTE mode behaviors remain intact.
"""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.knowledge_graph.engine import KnowledgeGraphEngine
from app.knowledge_graph.graph_storage import GraphStorage
from app.ai.memory.engine import LocalMemoryEngine
from app.ai.memory.configuration import MemoryConfiguration
from app.ai.memory.models import MemoryType, ContextPackage
from app.ai.copilot.orchestrator import CopilotOrchestrator
from app.ai.copilot.models import CopilotRequest, CopilotMode, CopilotResponse


@pytest.mark.anyio
async def test_scenario_a_graph_context_retrieval(tmp_path):
    """Scenario A: Persist User -> works_on -> Nova -> uses -> Blender and verify retrieval into planning context."""
    storage_dir = str(tmp_path / "scenario_a_kg")
    
    kg_engine = KnowledgeGraphEngine(storage_path=storage_dir)
    driver = kg_engine.storage.driver

    # 1. Persist entities & relationships
    await driver.add_entity({"id": "ent_user", "name": "User", "entity_type": "User"})
    await driver.add_entity({"id": "ent_nova", "name": "Nova", "entity_type": "Project"})
    await driver.add_entity({"id": "ent_blender", "name": "Blender", "entity_type": "Software"})

    await driver.add_relationship({
        "id": "rel_works_on",
        "source_id": "ent_user",
        "target_id": "ent_nova",
        "relationship_type": "works_on",
    })
    await driver.add_relationship({
        "id": "rel_uses",
        "source_id": "ent_nova",
        "target_id": "ent_blender",
        "relationship_type": "uses",
    })

    memory_config = MemoryConfiguration(vector_database="faiss", storage_path=storage_dir, similarity_threshold=0.0)
    memory_engine = LocalMemoryEngine(config=memory_config, graph_engine=kg_engine)
    orchestrator = CopilotOrchestrator(memory_engine=memory_engine)

    # 2. Query
    request = CopilotRequest(
        user_prompt="What project am I working on in Blender?",
        mode=CopilotMode.EXPLAIN,
        target_app="Blender",
    )
    response = await orchestrator.process_request(request)

    # 3. Verify retrieved graph context
    assert response.retrieved_memory_context is not None
    assert "[Knowledge Graph Context]" in response.retrieved_memory_context
    assert "User" in response.retrieved_memory_context
    assert "Nova" in response.retrieved_memory_context
    assert "Blender" in response.retrieved_memory_context
    assert "works_on" in response.retrieved_memory_context
    assert "uses" in response.retrieved_memory_context


@pytest.mark.anyio
async def test_scenario_b_unrelated_graph_filtering(tmp_path):
    """Scenario B: Persist target and unrelated entities, verify unrelated entities are excluded."""
    storage_dir = str(tmp_path / "scenario_b_kg")
    
    kg_engine = KnowledgeGraphEngine(storage_path=storage_dir)
    driver = kg_engine.storage.driver

    # Relevant graph
    await driver.add_entity({"id": "ent_user", "name": "User", "entity_type": "User"})
    await driver.add_entity({"id": "ent_nova", "name": "Nova", "entity_type": "Project"})
    await driver.add_relationship({"id": "rel1", "source_id": "ent_user", "target_id": "ent_nova", "relationship_type": "works_on"})

    # Unrelated graph
    await driver.add_entity({"id": "ent_pizza", "name": "Pizza", "entity_type": "Food"})
    await driver.add_entity({"id": "ent_oven", "name": "Oven", "entity_type": "Appliance"})
    await driver.add_relationship({"id": "rel2", "source_id": "ent_pizza", "target_id": "ent_oven", "relationship_type": "cooked_in"})

    memory_config = MemoryConfiguration(vector_database="faiss", storage_path=storage_dir, similarity_threshold=0.0)
    memory_engine = LocalMemoryEngine(config=memory_config, graph_engine=kg_engine)
    orchestrator = CopilotOrchestrator(memory_engine=memory_engine)

    request = CopilotRequest(
        user_prompt="What project am I working on?",
        mode=CopilotMode.EXPLAIN,
        target_app="Nova",
    )
    response = await orchestrator.process_request(request)

    assert response.retrieved_memory_context is not None
    assert "Nova" in response.retrieved_memory_context
    # Verify unrelated graph entities are excluded
    assert "Pizza" not in response.retrieved_memory_context
    assert "cooked_in" not in response.retrieved_memory_context


@pytest.mark.anyio
async def test_scenario_c_semantic_and_graph_coexistence(tmp_path):
    """Scenario C: Verify semantic memory and Knowledge Graph context coexist in the same ContextPackage."""
    storage_dir = str(tmp_path / "scenario_c_kg")
    
    kg_engine = KnowledgeGraphEngine(storage_path=storage_dir)
    driver = kg_engine.storage.driver
    await driver.add_entity({"id": "ent_user", "name": "User", "entity_type": "User"})
    await driver.add_entity({"id": "ent_nova", "name": "Nova", "entity_type": "Project"})
    await driver.add_relationship({"id": "r1", "source_id": "ent_user", "target_id": "ent_nova", "relationship_type": "develops"})

    memory_config = MemoryConfiguration(vector_database="faiss", storage_path=storage_dir, similarity_threshold=0.0)
    memory_engine = LocalMemoryEngine(config=memory_config, graph_engine=kg_engine)

    # Store semantic memory
    await memory_engine.store_memory(
        "User prefers Blender work in metric units.",
        MemoryType.CONVERSATION,
    )

    orchestrator = CopilotOrchestrator(memory_engine=memory_engine)

    request = CopilotRequest(
        user_prompt="Explain Nova project setup with metric units",
        mode=CopilotMode.EXPLAIN,
        target_app="Nova",
    )
    response = await orchestrator.process_request(request)

    # Verify both semantic memory and graph context present
    assert response.retrieved_memory_context is not None
    assert "[User / Conversation Memory]" in response.retrieved_memory_context
    assert "metric units" in response.retrieved_memory_context
    assert "[Knowledge Graph Context]" in response.retrieved_memory_context
    assert "develops" in response.retrieved_memory_context


@pytest.mark.anyio
async def test_scenario_d_restart_graph_persistence(tmp_path):
    """Scenario D: Restart/reinitialize graph storage and verify relationships remain available."""
    storage_dir = str(tmp_path / "scenario_d_kg")

    # 1. INITIALIZE & PERSIST GRAPH
    kg_1 = KnowledgeGraphEngine(storage_path=storage_dir)
    driver_1 = kg_1.storage.driver
    await driver_1.add_entity({"id": "ent_user", "name": "User", "entity_type": "User"})
    await driver_1.add_entity({"id": "ent_nova", "name": "Nova", "entity_type": "Project"})
    await driver_1.add_relationship({"id": "rel1", "source_id": "ent_user", "target_id": "ent_nova", "relationship_type": "works_on"})

    # 2. REINITIALIZE FROM DISK (Simulated restart)
    kg_2 = KnowledgeGraphEngine(storage_path=storage_dir)
    driver_2 = kg_2.storage.driver
    assert len(driver_2.entities) == 2
    assert len(driver_2.relationships) == 1

    memory_config = MemoryConfiguration(vector_database="faiss", storage_path=storage_dir, similarity_threshold=0.0)
    memory_engine = LocalMemoryEngine(config=memory_config, graph_engine=kg_2)
    orchestrator = CopilotOrchestrator(memory_engine=memory_engine)

    # 3. VERIFY RETRIEVAL FROM REINITIALIZED GRAPH
    request = CopilotRequest(
        user_prompt="What project am I working on?",
        mode=CopilotMode.EXPLAIN,
    )
    response = await orchestrator.process_request(request)

    assert response.retrieved_memory_context is not None
    assert "works_on" in response.retrieved_memory_context


@pytest.mark.anyio
async def test_scenario_e_forced_graph_failure_degradation():
    """Scenario E: Force graph retrieval failure and verify no fabricated relationships appear."""
    mock_kg = MagicMock()
    mock_kg.query_relevant_graph = AsyncMock(side_effect=RuntimeError("Graph DB offline"))

    memory_engine = LocalMemoryEngine(graph_engine=mock_kg)
    orchestrator = CopilotOrchestrator(memory_engine=memory_engine)

    request = CopilotRequest(
        user_prompt="Explain Nova layout",
        mode=CopilotMode.EXPLAIN,
        target_app="Nova",
    )
    response = await orchestrator.process_request(request)

    # Verify no fabricated graph relationships
    if response.retrieved_memory_context:
        assert "[Knowledge Graph Context]" not in response.retrieved_memory_context
    assert response.success is True


@pytest.mark.anyio
async def test_scenario_f_mode_behavior_preservation(tmp_path):
    """Scenario F: Verify EXPLAIN, GUIDE, EXECUTE behaviors remain intact with graph context."""
    storage_dir = str(tmp_path / "scenario_f_kg")
    
    kg_engine = KnowledgeGraphEngine(storage_path=storage_dir)
    driver = kg_engine.storage.driver
    await driver.add_entity({"id": "u1", "name": "User", "entity_type": "User"})
    await driver.add_entity({"id": "b1", "name": "Blender", "entity_type": "Software"})
    await driver.add_relationship({"id": "r1", "source_id": "u1", "target_id": "b1", "relationship_type": "uses"})

    memory_config = MemoryConfiguration(vector_database="faiss", storage_path=storage_dir, similarity_threshold=0.0)
    memory_engine = LocalMemoryEngine(config=memory_config, graph_engine=kg_engine)
    orchestrator = CopilotOrchestrator(memory_engine=memory_engine)

    # EXPLAIN MODE
    resp_explain = await orchestrator.process_request(
        CopilotRequest(user_prompt="Explain Blender uses", mode=CopilotMode.EXPLAIN, target_app="Blender")
    )
    assert resp_explain.success is True
    assert "Application Copilot Explanation" in resp_explain.explanation

    # GUIDE MODE
    resp_guide = await orchestrator.process_request(
        CopilotRequest(user_prompt="Guide me in Blender", mode=CopilotMode.GUIDE, target_app="Blender")
    )
    assert resp_guide.success is True
    assert len(resp_guide.guide_steps) >= 3

    # EXECUTE MODE
    resp_execute = await orchestrator.process_request(
        CopilotRequest(user_prompt="Click Blender setup", mode=CopilotMode.EXECUTE, target_app="Blender", parameters={"action_type": "click"})
    )
    assert resp_execute.success is True
    assert len(resp_execute.action_plan) == 1
