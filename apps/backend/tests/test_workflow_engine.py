"""Automated unit test suite verifying Workflow Orchestration Engine components.
"""

import pytest
from app.ai.gateway import IAIGateway
from app.core.dependency_container import resolve, register_ai_gateway_dependencies
from app.ai.workflow.workflow_engine import WorkflowEngine
from app.ai.workflow.models import WorkflowState, ApprovalRequest, ApprovalResult

@pytest.mark.anyio
async def test_workflow_engine_flows():
    """Verifies complete execution graphs, topological sorting, branching, checkpoints, and approvals."""
    try:
        register_ai_gateway_dependencies()
    except Exception:
        pass

    gateway = resolve(IAIGateway)
    engine = WorkflowEngine(
        event_bus=gateway.agents.event_bus,
        memory_engine=gateway.memory
    )

    # 1. Test creation and builder fallbacks
    wf = engine.builder.build_workflow("wf_test_1", "Compile website project")
    assert len(wf.steps) == 5
    assert wf.steps["step_arch"].agent_id == "architect"
    assert wf.state == WorkflowState.PENDING

    # 2. Test execution flow
    run_res = await engine.execute_workflow("Compile website project schemas")
    assert run_res["status"] == "success"
    assert run_res["state"] == "completed"

    # 3. Test branching
    branch = engine.branching_engine.select_branch("db_optimised == True", {"db_optimised": True})
    assert branch == "branch_true"

    # 4. Test checkpoints
    engine.save_checkpoint(run_res["workflow_id"])
    ckpts = engine.persistence.get_checkpoints(run_res["workflow_id"])
    assert len(ckpts) > 0

    # 5. Test recovery loader
    recovered = engine.recovery.recover_workflow(run_res["workflow_id"])
    assert recovered is not None
    assert recovered[0].workflow_id == run_res["workflow_id"]

    # 6. Test approvals gating
    req = ApprovalRequest(
        approval_id="app_test",
        workflow_id="wf_test_1",
        step_id="step_deploy",
        action="deploy",
        reason="Deploy schema tables"
    )
    engine.approvals.request_approval(req)
    assert engine.approvals.get_status("app_test") == "pending"

    result = ApprovalResult(
        approval_id="app_test",
        approved=True
    )
    engine.approvals.resolve_approval("app_test", result)
    assert engine.approvals.get_status("app_test") == "approved"
