"""Unit and integration tests for M3.4.20 Universal Agent Workforce, Autonomous AI Company & Multi-Agent Collaboration Platform.
"""

import pytest
from app.ai.agents.agent_bus import AgentMessageBus
from app.ai.agents.agent_learning_engine import AgentLearningEngine
from app.ai.agents.delegation_engine import TaskDelegationEngine
from app.ai.agents.engine import UniversalAgentWorkforceEngine
from app.ai.agents.manager import UniversalAgentWorkforceManager
from app.ai.agents.models import AgentDivision, AgentMessage, PeerReviewRequest
from app.ai.agents.peer_review_engine import PeerReviewEngine
from app.ai.agents.shared_memory import SharedAgentMemory
from app.ai.agents.voice_orchestrator import VoiceAgentOrchestrator


@pytest.mark.anyio
async def test_agent_message_bus():
    bus = AgentMessageBus()
    listeners = bus.list_active_listeners()
    assert len(listeners) == 9
    assert "EngineeringDivisionBus" in listeners

    msg = AgentMessage(sender_agent_id="ceo_agent", event_type="MISSION_STARTED")
    await bus.publish_message(msg)
    history = bus.get_message_history()
    assert len(history) == 1
    assert history[0].sender_agent_id == "ceo_agent"


@pytest.mark.anyio
async def test_task_delegation_engine_dag_decomposition():
    delegation = TaskDelegationEngine()
    dag = await delegation.decompose_goal("Build an Enterprise ERP system")
    assert len(dag.task_nodes) >= 5
    assert dag.task_nodes[0].assigned_agent_id == "SoftwareArchitectAgent"

    exec_res = await delegation.execute_mission_dag(dag)
    assert exec_res["status"] == "COMPLETED"
    assert exec_res["progress_percent"] == 100.0


@pytest.mark.anyio
async def test_peer_review_engine_quality_gates():
    review_engine = PeerReviewEngine()
    req = PeerReviewRequest(
        task_id="task_backend_01",
        author_agent_id="BackendEngineerAgent",
        content_to_review={"code": "def main(): pass"},
    )
    res = await review_engine.evaluate_deliverable(req)
    assert res.approved is True
    assert res.overall_quality_score >= 0.85
    assert "SecurityAuditAgent" in res.reviewer_comments


@pytest.mark.anyio
async def test_shared_memory_and_learning_engine():
    memory = SharedAgentMemory()
    memory.store("backend_architecture", {"framework": "FastAPI"}, author="SoftwareArchitectAgent")
    val = memory.retrieve("backend_architecture")
    assert val["framework"] == "FastAPI"

    learning = AgentLearningEngine()
    record = learning.record_learning("ERP_BUILD_PATTERN", ["Architect", "Implement", "Test"])
    assert record.pattern_name == "ERP_BUILD_PATTERN"


@pytest.mark.anyio
async def test_voice_agent_orchestrator():
    delegation = TaskDelegationEngine()
    review = PeerReviewEngine()
    orchestrator = VoiceAgentOrchestrator(delegation, review)

    res = await orchestrator.process_voice_mission("Nova, build a CRM backend platform")
    assert res["status"] == "DELIVERED"
    assert res["peer_review_approved"] is True
    assert len(res["reviewer_signoffs"]) >= 4


@pytest.mark.anyio
async def test_universal_agent_workforce_engine_master_facade():
    engine = UniversalAgentWorkforceEngine()
    agents = engine.list_all_agents()
    assert len(agents) == 67

    # Verify 9 divisions represented
    divisions = {a.division for a in agents}
    assert len(divisions) == 9

    health = engine.get_workforce_health()
    assert health.is_healthy is True
    assert health.total_registered_agents == 67

    voice_res = await engine.execute_voice_mission("Nova, deploy microservice stack")
    assert voice_res["status"] == "DELIVERED"
