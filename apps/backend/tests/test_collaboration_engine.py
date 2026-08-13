"""Automated unit test suite verifying collaboration engine flows.
"""

import pytest
from app.ai.gateway import IAIGateway
from app.core.dependency_container import resolve, register_ai_gateway_dependencies
from app.ai.collaboration.collaboration_engine import CollaborationEngine
from app.ai.collaboration.models import StructuredMessage, MessageType, MessagePriority

@pytest.mark.anyio
async def test_collaboration_engine_flows():
    """Verifies complete inter-agent communication, routing, negotiation, consensus, and handoff flows."""
    try:
        register_ai_gateway_dependencies()
    except Exception:
        pass

    gateway = resolve(IAIGateway)
    engine = CollaborationEngine(
        event_bus=gateway.agents.event_bus,
        memory_engine=gateway.memory
    )

    # 1. Test message routing & directed routing
    received = []
    async def test_cb(msg):
        received.append(msg)

    engine.bus.subscribe(MessageType.QUESTION.value, test_cb)
    
    question = StructuredMessage(
        sender="backend",
        receiver="database",
        correlation_id="cid_test_flows",
        message_type=MessageType.QUESTION,
        payload={"question_id": "q1", "question": "Optimize users query indices?"}
    )
    await engine.router.route(question)

    assert len(received) == 1
    assert received[0].correlation_id == "cid_test_flows"
    assert received[0].payload["question"] == "Optimize users query indices?"

    # 2. Test negotiation
    winner = await engine.negotiation.negotiate_ownership("db_task", ["postgres", "migration"])
    assert winner == "database"

    # 3. Test task handoff preserving context
    handoff_id = engine.handoff.initiate_handoff("task_1", "backend", "database", {"query": "SELECT email"})
    res = engine.handoff.complete_handoff(handoff_id, {"indexes": ["idx_email"]})
    assert res["query"] == "SELECT email"
    assert "idx_email" in res["indexes"]

    # 4. Test consensus voting
    consensus_res = await engine.consensus.seek_consensus("cid_test_flows", "Setup Postgres table schemas", "majority")
    assert consensus_res is True

    # 5. Test metrics & health checks
    health_status = engine.health.check_health()
    assert health_status["status"] == "healthy"

    # 6. Test voice summary generation & collaborative runs
    run_res = await engine.collaborate("Setup secure Postgres schemas database indexes migrations")
    assert run_res["status"] == "success"
    assert "voice_summary" in run_res
    assert "elected_leader" in run_res

    # 7. Test gateway integration
    gateway_res = await gateway.collaborate("Build secure API authentication database tables")
    assert gateway_res["status"] == "success"
    assert "voice_summary" in gateway_res
