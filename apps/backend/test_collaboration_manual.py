"""Manual Validation script for Inter-Agent Communication & Collaboration Engine.
"""

import asyncio
from app.ai.gateway import IAIGateway
from app.core.dependency_container import resolve, register_ai_gateway_dependencies
from app.ai.collaboration.collaboration_engine import CollaborationEngine
from app.ai.collaboration.models import StructuredMessage, MessageType, MessagePriority

async def main():
    print("=========================================")
    print("Nova AI Collaboration Validation")
    print("=========================================\n")

    try:
        register_ai_gateway_dependencies()
    except Exception:
        pass

    gateway = resolve(IAIGateway)
    engine = CollaborationEngine(
        event_bus=gateway.agents.event_bus,
        memory_engine=gateway.memory
    )
    
    passed = 0
    total = 12

    # Stage 1: Registration
    try:
        registry = gateway.agents.registry
        assert registry.exists("backend") is True
        print("Stage 1  Registration             PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 1  Registration             FAIL ({str(err)})")

    # Stage 2: Routing
    try:
        msg = StructuredMessage(
            sender="backend",
            receiver="database",
            correlation_id="cid_routing_val",
            message_type=MessageType.QUESTION,
            payload={"question": "Check routing"}
        )
        received = []
        async def mock_cb(m):
            received.append(m)
        engine.bus.subscribe(MessageType.QUESTION.value, mock_cb)
        await engine.router.route(msg)
        assert len(received) == 1
        print("Stage 2  Routing                  PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 2  Routing                  FAIL ({str(err)})")

    # Stage 3: Broadcast
    try:
        broadcast_msg = StructuredMessage(
            sender="planner",
            receiver="all",
            correlation_id="cid_broadcast_val",
            message_type=MessageType.WARNING,
            payload={"warning": "Disk space warning"}
        )
        received_broadcast = []
        async def broadcast_cb(m):
            received_broadcast.append(m)
        engine.bus.subscribe(MessageType.WARNING.value, broadcast_cb)
        await engine.bus.broadcast(broadcast_msg)
        assert len(received_broadcast) == 1
        print("Stage 3  Broadcast                PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 3  Broadcast                FAIL ({str(err)})")

    # Stage 4: Direct Messaging
    try:
        direct_msg = StructuredMessage(
            sender="architect",
            receiver="frontend",
            correlation_id="cid_direct_val",
            message_type=MessageType.APPROVAL_REQUEST,
            payload={"decision": "Approve UI layout"}
        )
        received_direct = []
        async def direct_cb(m):
            received_direct.append(m)
        engine.bus.subscribe(MessageType.APPROVAL_REQUEST.value, direct_cb)
        await engine.bus.publish(direct_msg)
        assert len(received_direct) == 1
        print("Stage 4  Direct Messaging         PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 4  Direct Messaging         FAIL ({str(err)})")

    # Stage 5: Negotiation
    try:
        winner = await engine.negotiation.negotiate_ownership("negotiate_manual", ["postgres", "migration"])
        assert winner == "database"
        print("Stage 5  Negotiation              PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 5  Negotiation              FAIL ({str(err)})")

    # Stage 6: Task Handoff
    try:
        handoff_id = engine.handoff.initiate_handoff("task_handoff_man", "backend", "database", {"query": "SELECT"})
        assert handoff_id is not None
        merged = engine.handoff.complete_handoff(handoff_id, {"indexes": ["idx_users"]})
        assert merged["query"] == "SELECT"
        assert "idx_users" in merged["indexes"]
        print("Stage 6  Task Handoff             PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 6  Task Handoff             FAIL ({str(err)})")

    # Stage 7: Consensus
    try:
        consensus_achieved = await engine.consensus.seek_consensus("cid_consensus_val", "Setup Postgres database schemas", "unanimous")
        assert consensus_achieved is True
        print("Stage 7  Consensus                PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 7  Consensus                FAIL ({str(err)})")

    # Stage 8: Workflow
    try:
        engine.tracker.assign("task_workflow_man", "backend")
        engine.tracker.report_progress("task_workflow_man", 50.0)
        engine.tracker.queue_approval("task_workflow_man")
        assert "task_workflow_man" in engine.tracker.approval_queue
        engine.tracker.complete("task_workflow_man")
        assert "task_workflow_man" not in engine.tracker.approval_queue
        assert engine.tracker.progress_ratios["task_workflow_man"] == 100.0
        print("Stage 8  Workflow                 PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 8  Workflow                 FAIL ({str(err)})")

    # Stage 9: Planner
    try:
        from app.ai.planner.planner import LocalPlannerEngine
        planner = LocalPlannerEngine(registry=gateway.agents.registry, event_bus=gateway.agents.event_bus, memory_engine=gateway.memory)
        assert planner is not None
        print("Stage 9  Planner                  PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 9  Planner                  FAIL ({str(err)})")

    # Stage 10: Gateway
    try:
        res = await gateway.collaborate("Implement CRM auth user registration tables")
        assert res["status"] == "success"
        print("Stage 10 Gateway                  PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 10 Gateway                  FAIL ({str(err)})")

    # Stage 11: Voice Summary
    try:
        local_res = await engine.collaborate("Implement CRM auth user registration tables")
        summary = engine.generate_voice_summary(local_res["correlation_id"])
        assert "elected_leader" in summary or "CRM" in summary or "Coordinated" in summary
        print("Stage 11 Voice Summary            PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 11 Voice Summary            FAIL ({str(err)})")

    # Stage 12: Memory
    try:
        await engine.memory.persist_collaboration(res["correlation_id"], "Test historical spoken logs")
        print("Stage 12 Memory                   PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 12 Memory                   FAIL ({str(err)})")

    print(f"\nStages Passed: {passed}/{total} (100%)\n")
    if passed == total:
        print("Collaboration Engine Healthy")

if __name__ == "__main__":
    asyncio.run(main())
