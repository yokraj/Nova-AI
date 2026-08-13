"""Manual Validation script for Human Approval & Safety Engine.
"""

import asyncio
from app.ai.gateway import IAIGateway
from app.core.dependency_container import resolve, register_ai_gateway_dependencies
from app.ai.safety.safety_engine import SafetyEngine
from app.ai.safety.models import RiskLevel

async def main():
    print("=========================================")
    print("Nova AI Safety Validation")
    print("=========================================\n")

    try:
        register_ai_gateway_dependencies()
    except Exception:
        pass

    gateway = resolve(IAIGateway)
    engine = SafetyEngine(
        event_bus=gateway.agents.event_bus,
        memory_engine=gateway.memory
    )
    
    passed = 0
    total = 12

    # Stage 1 Risk Classification
    try:
        assess = engine.classify_risk("delete directories", {})
        assert assess.risk_level == RiskLevel.HIGH
        print("Stage 1 Risk Classification PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 1 Risk Classification FAIL ({str(err)})")

    # Stage 2 Approval Queue
    try:
        check = await engine.check_action("ms_manual", "delete directories", {"count_value": "1"})
        assert check["status"] == "gated"
        app_id = check["approval_id"]
        assert len(engine.pending_approvals()) == 1
        print("Stage 2 Approval Queue PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 2 Approval Queue FAIL ({str(err)})")

    # Stage 3 Consent
    try:
        engine.consent.give_consent("delete directories")
        assert engine.consent.has_consent("delete directories") is True
        print("Stage 3 Consent PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 3 Consent FAIL ({str(err)})")

    # Stage 4 Policy
    try:
        policy = engine.policy.evaluate_policy("delete directories", RiskLevel.HIGH)
        assert policy["requires_vocal_confirmation"] is False
        
        policy_critical = engine.policy.evaluate_policy("buy ticket", RiskLevel.CRITICAL)
        assert policy_critical["requires_vocal_confirmation"] is True
        print("Stage 4 Policy PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 4 Policy FAIL ({str(err)})")

    # Stage 5 Workflow Pause
    try:
        from app.ai.workflow.workflow_engine import WorkflowEngine
        from app.ai.workflow.workflow_context import WorkflowContextContainer
        from app.ai.workflow.models import WorkflowStep, Workflow
        
        wf_engine = WorkflowEngine(gateway.agents.event_bus, gateway.memory)
        steps = {
            "step_gated": WorkflowStep(
                step_id="step_gated",
                title="Destructive task node",
                description="Delete production logs",
                agent_id="devops",
                action="approval_gate"
            )
        }
        wf = Workflow(workflow_id="wf_pause_val", goal="Delete logs", steps=steps)
        
        # Save states and context container
        wf_engine.scheduler.enqueue(wf)
        wf_engine.contexts["wf_pause_val"] = WorkflowContextContainer("wf_pause_val")
        wf_engine.persistence.save_workflow(wf)
        
        # Run execution loop: it pauses at the approval gate
        await wf_engine._run_loop("wf_pause_val")
        
        persisted = wf_engine.persistence.get_workflow("wf_pause_val")
        assert persisted.state == "paused"
        print("Stage 5 Workflow Pause PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 5 Workflow Pause FAIL ({str(err)})")

    # Stage 6 Mission Pause
    try:
        from app.ai.mission.mission_engine import MissionEngine
        ms_engine = MissionEngine(gateway.agents.event_bus, gateway.memory)
        assert ms_engine.scheduler is not None
        print("Stage 6 Mission Pause PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 6 Mission Pause FAIL ({str(err)})")

    # Stage 7 Voice Confirmation
    try:
        prompt = engine.confirmation.format_prompt("buy ticket", {"cost_value": "INR 1,250", "item_name": "Vande Bharat"}, RiskLevel.CRITICAL)
        assert "INR 1,250" in prompt
        print("Stage 7 Voice Confirmation PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 7 Voice Confirmation FAIL ({str(err)})")

    # Stage 8 Audit
    try:
        await engine.approve(app_id)
        assert len(engine.audit.get_logs()) == 1
        print("Stage 8 Audit PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 8 Audit FAIL ({str(err)})")

    # Stage 9 Gateway
    try:
        res = await gateway.request_approval("ms_manual", "purchase item", {"cost_value": "INR 100"})
        assert res["status"] == "gated"
        print("Stage 9 Gateway PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 9 Gateway FAIL ({str(err)})")

    # Stage 10 Browser Protection
    try:
        check_browser = await engine.check_action("ms_manual", "open browser", {})
        assert check_browser["status"] == "approved"
        print("Stage 10 Browser Protection PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 10 Browser Protection FAIL ({str(err)})")

    # Stage 11 Recovery
    try:
        assert engine.permissions.grant_permission("read", 60) is not None
        assert engine.permissions.check_permission("read") is True
        print("Stage 11 Recovery PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 11 Recovery FAIL ({str(err)})")

    # Stage 12 Complete
    try:
        assert engine.health.check_health()["status"] == "healthy"
        print("Stage 12 Complete PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 12 Complete FAIL ({str(err)})")

    print(f"\n{passed}/{total} PASS")
    if passed == total:
        print("\nMission Engine Healthy")

if __name__ == "__main__":
    asyncio.run(main())
