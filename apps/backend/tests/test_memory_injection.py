"""Focused Tests for AgentRuntime Real Memory Context Injection (F1.56C).

Proves:
A. Store preference -> AgentRuntime request retrieves preference into planning context.
B. Store unrelated memories -> irrelevant memories are filtered out of planning context.
C. Restart/reinitialize memory layer -> preference remains retrievable by AgentRuntime.
D. Forced memory retrieval failure -> no fabricated memory, request degrades safely.
E. EXPLAIN, GUIDE, EXECUTE modes behavior verification with and without memory context.
"""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.ai.copilot.orchestrator import CopilotOrchestrator
from app.ai.copilot.models import CopilotRequest, CopilotMode, CopilotResponse
from app.ai.memory.engine import LocalMemoryEngine
from app.ai.memory.configuration import MemoryConfiguration
from app.ai.memory.models import MemoryType, ContextPackage, RetrievalResult


@pytest.mark.anyio
async def test_scenario_a_user_preference_retrieval(tmp_path):
    """Scenario A: Store user preference and verify AgentRuntime context retrieval during planning."""
    storage_dir = str(tmp_path / "scenario_a_memory")
    config = MemoryConfiguration(
        vector_database="faiss",
        storage_path=storage_dir,
        similarity_threshold=0.0,
    )
    memory_engine = LocalMemoryEngine(config=config)

    # 1. Store preference
    await memory_engine.store_memory(
        "User prefers Blender work in metric units.",
        MemoryType.CONVERSATION,
        metadata={"category": "user_preference"},
    )

    orchestrator = CopilotOrchestrator(memory_engine=memory_engine)

    # 2. Issue request
    request = CopilotRequest(
        user_prompt="Create a Blender object using my preferred units.",
        mode=CopilotMode.EXECUTE,
        target_app="Blender",
        parameters={"action_type": "create_object"},
    )

    response = await orchestrator.process_request(request)

    # 3. Verify retrieved memory context is present and contains preference
    assert response.retrieved_memory_context is not None
    assert "=== RETRIEVED PERSISTENT MEMORY CONTEXT ===" in response.retrieved_memory_context
    assert "metric units" in response.retrieved_memory_context
    # Verify parameter injection from retrieved context
    assert response.action_plan[0].selector.get("unit_system") == "metric"


@pytest.mark.anyio
async def test_scenario_b_irrelevant_memory_filtering(tmp_path):
    """Scenario B: Store unrelated memory and verify irrelevant memories are not injected."""
    storage_dir = str(tmp_path / "scenario_b_memory")
    config = MemoryConfiguration(
        vector_database="faiss",
        storage_path=storage_dir,
        similarity_threshold=0.7,
    )
    memory_engine = LocalMemoryEngine(config=config)

    # 1. Store unrelated memory
    await memory_engine.store_memory(
        "User likes baking pizza on Sundays with sourdough crust.",
        MemoryType.CONVERSATION,
        metadata={"category": "hobbies"},
    )

    orchestrator = CopilotOrchestrator(memory_engine=memory_engine)

    # 2. Issue unrelated request
    request = CopilotRequest(
        user_prompt="Create a Blender 3D mesh object",
        mode=CopilotMode.EXPLAIN,
        target_app="Blender",
    )

    response = await orchestrator.process_request(request)

    # 3. Verify irrelevant memory is NOT in planning context
    if response.retrieved_memory_context:
        assert "pizza" not in response.retrieved_memory_context
        assert "sourdough" not in response.retrieved_memory_context


@pytest.mark.anyio
async def test_scenario_c_restart_persistence_retrieval(tmp_path):
    """Scenario C: Reinitialize memory layer and verify preference remains retrievable by AgentRuntime."""
    storage_dir = str(tmp_path / "scenario_c_memory")
    config = MemoryConfiguration(
        vector_database="faiss",
        storage_path=storage_dir,
        similarity_threshold=0.0,
    )

    # 1. INITIALIZE & STORE MEMORY
    engine_1 = LocalMemoryEngine(config=config)
    await engine_1.store_memory(
        "User prefers Blender work in metric units.",
        MemoryType.CONVERSATION,
        metadata={"category": "preference"},
    )
    assert await engine_1.count_memories() == 1

    # 2. REINITIALIZE MEMORY ENGINE FROM DISK (Simulating process restart)
    engine_2 = LocalMemoryEngine(config=config)
    assert await engine_2.count_memories() == 1

    orchestrator = CopilotOrchestrator(memory_engine=engine_2)

    # 3. VERIFY AGENTRUNTIME RETRIEVES MEMORY FROM REINITIALIZED ENGINE
    request = CopilotRequest(
        user_prompt="Create a Blender object using my preferred units.",
        mode=CopilotMode.GUIDE,
        target_app="Blender",
    )
    response = await orchestrator.process_request(request)

    assert response.retrieved_memory_context is not None
    assert "metric units" in response.retrieved_memory_context


@pytest.mark.anyio
async def test_scenario_d_forced_retrieval_failure_fallback():
    """Scenario D: Force memory retrieval failure and verify no fake memory & safe request execution."""
    mock_memory_engine = MagicMock()
    # Force retrieval failure exception
    mock_memory_engine.retrieve_context = AsyncMock(side_effect=RuntimeError("Vector Store corrupted or unreadable"))

    orchestrator = CopilotOrchestrator(memory_engine=mock_memory_engine)

    request = CopilotRequest(
        user_prompt="Explain Blender controls",
        mode=CopilotMode.EXPLAIN,
        target_app="Blender",
    )

    response = await orchestrator.process_request(request)

    # Verify no fabricated memory
    assert response.retrieved_memory_context is None
    # Verify request still succeeded gracefully according to safety rules
    assert response.success is True
    assert "Application Copilot Explanation" in response.explanation


@pytest.mark.anyio
async def test_scenario_e_mode_behavior_preservation(tmp_path):
    """Scenario E: Verify EXPLAIN, GUIDE, EXECUTE behaviors with and without memory context."""
    storage_dir = str(tmp_path / "scenario_e_memory")
    config = MemoryConfiguration(
        vector_database="faiss",
        storage_path=storage_dir,
        similarity_threshold=0.0,
    )
    memory_engine = LocalMemoryEngine(config=config)
    await memory_engine.store_memory(
        "User prefers dark theme and metric units.",
        MemoryType.CONVERSATION,
    )

    orchestrator = CopilotOrchestrator(memory_engine=memory_engine)

    # 1. EXPLAIN MODE
    req_explain = CopilotRequest(user_prompt="Explain UI layout", mode=CopilotMode.EXPLAIN, target_app="Blender")
    resp_explain = await orchestrator.process_request(req_explain)
    assert resp_explain.success is True
    assert "Application Copilot Explanation" in resp_explain.explanation

    # 2. GUIDE MODE
    req_guide = CopilotRequest(user_prompt="Guide me through layout setup", mode=CopilotMode.GUIDE, target_app="Blender")
    resp_guide = await orchestrator.process_request(req_guide)
    assert resp_guide.success is True
    assert len(resp_guide.guide_steps) >= 3

    # 3. EXECUTE MODE
    req_execute = CopilotRequest(
        user_prompt="Execute layout change",
        mode=CopilotMode.EXECUTE,
        target_app="Blender",
        parameters={"action_type": "click", "target_label": "Setup Button"},
    )
    resp_execute = await orchestrator.process_request(req_execute)
    assert resp_execute.success is True
    assert len(resp_execute.action_plan) == 1
    # Verify execution memory write back
    assert await memory_engine.count_memories() >= 2
