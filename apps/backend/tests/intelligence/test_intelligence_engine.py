"""Unit and Integration Tests for Nova AI Universal Intelligence Engine (Nova Brain).

Validates all 15 core sub-engines and master UniversalIntelligenceEngine orchestrator.
"""

import asyncio
import pytest

from app.intelligence import (
    IntelligenceConfig,
    UniversalIntelligenceEngine,
    TaskPlanner,
    ReasoningEngine,
    KnowledgeEngine,
    MemoryEngine,
    ModelRouter,
    ToolRouter,
    AgentRouter,
    VerificationEngine,
    ReflectionEngine,
    ContextManager,
    DecisionEngine,
    LearningEngine,
    ConversationEngine,
    PromptManager,
    PersonalityEngine,
    IntentDetector,
    TaskDecomposer,
)


@pytest.fixture
def config():
    return IntelligenceConfig()


@pytest.fixture
def engine(config):
    return UniversalIntelligenceEngine(config=config)


def test_universal_intelligence_engine_end_to_end(engine):
    """Test full request processing pipeline through UniversalIntelligenceEngine."""
    async def _test():
        result = await engine.process_request(
            prompt="Build a hospital management system architecture with PostgreSQL and React",
            conversation_id="conv-test-01",
        )

        assert "response" in result
        assert result["conversation_id"] == "conv-test-01"
        assert result["intent"]["category"] == "multi_step_planning"
        assert result["decisions"]["need_multiple_agents"] is True
        assert result["plan"] is not None
        assert result["plan"]["subtask_count"] == 8
        assert result["verification"]["is_valid"] is True
        assert result["reflection"] is not None

    asyncio.run(_test())


def test_universal_intelligence_engine_streaming(engine):
    """Test streaming token output generator."""
    async def _test():
        tokens = []
        async for chunk in engine.stream_request("Explain quantum computing principles", conversation_id="conv-stream-01"):
            tokens.append(chunk)

        assert len(tokens) > 0
        full_streamed_text = "".join(tokens)
        assert len(full_streamed_text) > 20

    asyncio.run(_test())


def test_conversation_engine_domains():
    """Test multi-domain dialogue handling and clarification logic."""
    async def _test():
        conv_engine = ConversationEngine()

        # 1. Standard conversation turn
        res = await conv_engine.process_turn("How does backpropagation work in neural networks?", conversation_id="conv-domain-01")
        assert res["needs_clarification"] is False
        assert "neural networks" in res["response"]

        # 2. Clarification request for vague input
        res_vague = await conv_engine.process_turn("Physics", conversation_id="conv-domain-01")
        assert res_vague["needs_clarification"] is True

        # 3. Summarization
        summary = await conv_engine.summarize_conversation("conv-domain-01")
        assert "conv-domain-01" in summary

    asyncio.run(_test())


def test_task_planner_decomposition():
    """Test TaskPlanner goal analysis, tool/agent selection, and plan creation."""
    planner = TaskPlanner()
    goal = "Build a distributed Python microservice backend for SQL database analytics"

    plan = planner.create_plan(goal)
    assert plan["complexity_score"] >= 3
    assert plan["subtask_count"] >= 3
    assert "primary_agent" in plan
    assert len(plan["required_tools"]) > 0
    assert len(plan["dependencies"]) == plan["subtask_count"]


def test_reasoning_engine():
    """Test Chain-of-Thought reasoning, option comparison, and 5-Whys RCA."""
    async def _test():
        reasoner = ReasoningEngine()

        # 1. Step-by-step reasoning
        cot = await reasoner.step_by_step_reasoning("Optimize database query latency under 10k QPS")
        assert len(cot["steps"]) == 4

        # 2. Option comparison
        comp = await reasoner.compare_options("PostgreSQL", "MongoDB", ["ACID Compliance", "Query Performance"])
        assert "option_a" in comp
        assert "recommendation" in comp

        # 3. 5-Whys Root Cause Analysis
        rca = await reasoner.analyze_root_cause("WebSocket Disconnection Storm")
        assert len(rca["whys"]) == 5
        assert "Root Cause" in rca["root_cause"]

    asyncio.run(_test())


def test_knowledge_engine_retrieval():
    """Test hybrid knowledge retrieval and document ingestion."""
    async def _test():
        knowledge = KnowledgeEngine()

        retrieved = await knowledge.retrieve_hybrid_knowledge("system architecture design", top_k=5, enable_web=True)
        assert retrieved["retrieved_count"] >= 2
        assert "context_summary" in retrieved

        ingest = await knowledge.ingest_document("docs/architecture/SYSTEM_ARCHITECTURE.md", "markdown")
        assert ingest["status"] == "success"

    asyncio.run(_test())


def test_memory_engine_multi_tiered():
    """Test short-term, long-term, user preferences, and searchable memory tiers."""
    async def _test():
        mem = MemoryEngine()

        # 1. Short-term
        await mem.add_short_term("user", "My favorite programming language is Python", "conv-mem-01")
        history = await mem.get_recent_conversation_history("conv-mem-01")
        assert len(history) == 1

        # 2. Long-term
        await mem.store_long_term("user_role", "Principal Architect", "user_profile")

        # 3. User Preferences
        await mem.update_user_preferences({"theme": "dark", "tab_size": 4})
        prefs = await mem.get_user_preferences()
        assert prefs["theme"] == "dark"

        # 4. Searchable Memory
        search_res = await mem.search_memory("Python")
        assert len(search_res) > 0

    asyncio.run(_test())


def test_model_router():
    """Test task-based LLM model and provider routing."""
    router = ModelRouter()

    # Coding task
    code_target = router.select_model(task_type="code_generation", prefer_local=True)
    assert "coder" in code_target["model"].lower() or "qwen" in code_target["model"].lower()

    # Reasoning task
    reason_target = router.select_model(task_type="deep_reasoning", prefer_local=True)
    assert "deepseek" in reason_target["model"].lower() or "r1" in reason_target["model"].lower()


def test_tool_router():
    """Test automatic tool selection for query requirements."""
    router = ToolRouter()

    tools = router.evaluate_tool_needs("Calculate sqrt of 144 and execute python script to verify")
    tool_names = [t["tool"] for t in tools]
    assert "calculator" in tool_names
    assert "python_interpreter" in tool_names


def test_agent_router():
    """Test workforce agent assignment."""
    router = AgentRouter()

    agent_b = router.select_agent("Implement FastAPI backend endpoints for dashboard")
    assert agent_b["agent_id"] == "backend_agent"

    agent_f = router.select_agent("Build React UI components with CSS glassmorphism")
    assert agent_f["agent_id"] == "frontend_agent"


def test_verification_and_reflection():
    """Test verification and reflection pre-response self-critique engines."""
    async def _test():
        verifier = VerificationEngine()
        reflector = ReflectionEngine()

        # Verification
        v_res = await verifier.verify_output("The memory usage is 45.2%.", grounding_context="memory: 45.2%")
        assert v_res["is_valid"] is True

        # Reflection
        r_res = await reflector.reflect_and_refine("Short draft.", "Provide detailed architecture breakdown")
        assert "refined_response" in r_res
        assert len(r_res["weaknesses_identified"]) > 0

    asyncio.run(_test())


def test_context_manager_compression():
    """Test multi-dimensional context assembly and compression windowing."""
    small_config = IntelligenceConfig(context_window_size=100)
    ctx_mgr = ContextManager(config=small_config)

    history = [{"role": "user", "content": f"Message turn {i} with additional context and text payload"} for i in range(10)]
    ctx = ctx_mgr.assemble_full_context(history)

    assert "conversation_history" in ctx
    assert len(ctx["conversation_history"]) < 10  # Compressed into summary + 4 recent turns


def test_decision_engine():
    """Test autonomous capability decision evaluation."""
    decision_engine = DecisionEngine()

    decisions = decision_engine.evaluate_request("Search web and run python calculation for market trends", conversation_length=5)
    assert decisions["need_memory"] is True
    assert decisions["need_tools"] is True
    assert decisions["need_internet"] is True
