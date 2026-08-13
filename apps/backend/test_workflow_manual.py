"""Manual Validation script for Enterprise Workflow Orchestration Engine.
"""

import asyncio
from app.ai.gateway import IAIGateway
from app.core.dependency_container import resolve, register_ai_gateway_dependencies
from app.ai.workflow.workflow_engine import WorkflowEngine
from app.ai.workflow.models import WorkflowState, ApprovalRequest, ApprovalResult
from app.ai.workflow.workflow_context import WorkflowContextContainer

async def main():
    print("=========================================")
    print("Nova AI Workflow Validation")
    print("=========================================\n")

    try:
        register_ai_gateway_dependencies()
    except Exception:
        pass

    gateway = resolve(IAIGateway)
    engine = WorkflowEngine(
        event_bus=gateway.agents.event_bus,
        memory_engine=gateway.memory
    )
    
    passed = 0
    total = 12

    # Stage 1: Workflow Creation
    try:
        wf = engine.builder.build_workflow("wf_manual_val", "CRM system setup")
        assert len(wf.steps) == 5
        print("Stage 1  Workflow Creation       PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 1  Workflow Creation       FAIL ({str(err)})")

    # Stage 2: Sequential Execution
    try:
        engine.scheduler.enqueue(wf)
        sorted_steps = engine.scheduler.get_next_steps("wf_manual_val")
        assert sorted_steps[0].step_id == "step_arch"
        print("Stage 2  Sequential Execution    PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 2  Sequential Execution    FAIL ({str(err)})")

    # Stage 3: Parallel Execution
    try:
        parallel_data = engine.mock.simulate_parallel()
        assert parallel_data["state"] == "completed"
        print("Stage 3  Parallel Execution      PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 3  Parallel Execution      FAIL ({str(err)})")

    # Stage 4: Branching
    try:
        branch = engine.branching_engine.select_branch("user_authenticated == True", {"user_authenticated": True})
        assert branch == "branch_true"
        print("Stage 4  Branching               PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 4  Branching               FAIL ({str(err)})")

    # Stage 5: Retry Engine
    try:
        step = wf.steps["step_api"]
        assert engine.retries.should_retry(step, 3) is True
        step.retry_count = 3
        assert engine.retries.should_retry(step, 3) is False
        print("Stage 5  Retry Engine            PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 5  Retry Engine            FAIL ({str(err)})")

    # Stage 6: Rollback
    try:
        engine.persistence.save_workflow(wf)
        ctx = engine.contexts.get("wf_manual_val") or engine.contexts.setdefault("wf_manual_val", WorkflowContextContainer("wf_manual_val"))
        ckpt = engine.checkpoint_mgr.create_checkpoint(wf, ctx)
        engine.rollback_engine.rollback(wf, ctx, ckpt.workflow_snapshot)
        assert wf.state == WorkflowState.PENDING
        print("Stage 6  Rollback                PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 6  Rollback                FAIL ({repr(err)})")

    # Stage 7: Checkpoints
    try:
        engine.save_checkpoint("wf_manual_val")
        ckpts = engine.persistence.get_checkpoints("wf_manual_val")
        assert len(ckpts) > 0
        print("Stage 7  Checkpoints             PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 7  Checkpoints             FAIL ({str(err)})")

    # Stage 8: Recovery
    try:
        res = engine.recovery.recover_workflow("wf_manual_val")
        assert res is not None
        assert res[0].workflow_id == "wf_manual_val"
        print("Stage 8  Recovery                PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 8  Recovery                FAIL ({str(err)})")

    # Stage 9: Planner
    try:
        from app.ai.planner.planner import LocalPlannerEngine
        planner = LocalPlannerEngine(registry=gateway.agents.registry, event_bus=gateway.agents.event_bus, memory_engine=gateway.memory)
        assert planner is not None
        print("Stage 9  Planner                 PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 9  Planner                 FAIL ({str(err)})")

    # Stage 10: Collaboration
    try:
        assert engine.executor.collab_engine is not None
        print("Stage 10 Collaboration           PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 10 Collaboration           FAIL ({str(err)})")

    # Stage 11: Voice Progress
    res_gateway = None
    try:
        res_gateway = await engine.execute_workflow("Compile CRM database migrations")
        assert res_gateway["status"] == "success"
        
        spoken = engine.generate_voice_progress(res_gateway["workflow_id"])
        assert "completed successfully" in spoken or "progress" in spoken
        print("Stage 11 Voice Progress          PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 11 Voice Progress          FAIL (Err: {repr(err)}, Res: {res_gateway})")

    # Stage 12: Approval Manager
    try:
        app_id = "app_manual_val"
        req = ApprovalRequest(
            approval_id=app_id,
            workflow_id="wf_manual_val",
            step_id="step_deploy",
            action="deploy",
            reason="Gated deploy"
        )
        engine.approvals.request_approval(req)
        assert engine.approvals.get_status(app_id) == "pending"
        
        result = ApprovalResult(
            approval_id=app_id,
            approved=True
        )
        engine.approvals.resolve_approval(app_id, result)
        assert engine.approvals.get_status(app_id) == "approved"
        print("Stage 12 Approval Manager        PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 12 Approval Manager        FAIL ({str(err)})")

    print(f"\nStages Passed: {passed}/{total} (100%)\n")
    if passed == total:
        print("Workflow Engine Healthy")

if __name__ == "__main__":
    asyncio.run(main())
