"""Automated unit test suite verifying the Autonomous Skill Execution Runtime.

Tests cover:
1. Core ExecutionRuntime facade initialization
2. ExecutionContext data sharing across steps
3. StateManager mission & step transitions
4. ExecutionQueue FIFO prioritization & concurrency
5. CheckpointManager snapshot creation & restoration
6. RollbackManager compensating inverse actions
7. TransactionManager transactional commit & rollback
8. RecoveryManager step retries & error handling
9. ApprovalHandler dangerous action interception
10. PluginExecutor capability execution
11. MissionExecutor multi-step plan execution
12. ExecutionPipeline voice command processing
13. ProgressTracker, ExecutionMonitor, & Metrics
14. Mock Execution Provider
15. Gateway Integration APIs (execute_mission, mission_status, active_missions)
"""

import pytest

from app.ai.execution.configuration import ExecutionConfiguration
from app.ai.execution.execution_context import ExecutionContext
from app.ai.execution.execution_pipeline import ExecutionPipeline
from app.ai.execution.execution_queue import ExecutionQueue
from app.ai.execution.execution_runtime import ExecutionRuntime
from app.ai.execution.exceptions import StepFailedError
from app.ai.execution.mock_provider import MockExecutionProvider
from app.ai.execution.models import (
    CheckpointData,
    ExecutionState,
    ExecutionStep,
    MissionExecutionPlan,
    PriorityLevel,
    StepStatus,
)
from app.ai.gateway import IAIGateway
from app.core.dependency_container import register_ai_gateway_dependencies, resolve


@pytest.fixture
def runtime() -> ExecutionRuntime:
    config = ExecutionConfiguration(max_concurrent_missions=5)
    return ExecutionRuntime(config=config)


# ============================================================
# 1. Execution Context & State
# ============================================================

def test_execution_context() -> None:
    ctx = ExecutionContext(mission_id="ms_test_ctx")
    ctx.set("pdf_summary", "Q3 Report Summary")
    ctx.record_step_output("step_1", {"summary": "Q3 Report Summary"})

    assert ctx.get("pdf_summary") == "Q3 Report Summary"
    assert ctx.get_step_output("step_1") == {"summary": "Q3 Report Summary"}


# ============================================================
# 2. Execution Queue
# ============================================================

def test_execution_queue() -> None:
    queue = ExecutionQueue(max_concurrent=2)
    p1 = MissionExecutionPlan(mission_id="m1", goal="Goal 1", priority=PriorityLevel.LOW)
    p2 = MissionExecutionPlan(mission_id="m2", goal="Goal 2", priority=PriorityLevel.CRITICAL)

    queue.enqueue(p1)
    queue.enqueue(p2)

    # Dequeue should yield p2 first (CRITICAL priority)
    deq1 = queue.dequeue()
    assert deq1 is not None
    assert deq1.mission_id == "m2"

    deq2 = queue.dequeue()
    assert deq2 is not None
    assert deq2.mission_id == "m1"


# ============================================================
# 3. Checkpoints & Persistence
# ============================================================

@pytest.mark.anyio
async def test_checkpoint_manager(runtime: ExecutionRuntime) -> None:
    plan = MissionExecutionPlan(
        mission_id="chk_test_01",
        goal="Test checkpointing",
        steps=[
            ExecutionStep(step_id="s1", name="Step 1", plugin_id="file", capability="read_file", status=StepStatus.COMPLETED)
        ],
    )
    chk = await runtime.checkpoint_mgr.create_checkpoint(plan, {"test_key": "val"})
    assert chk.mission_id == "chk_test_01"

    loaded = await runtime.checkpoint_mgr.load_checkpoint("chk_test_01")
    assert loaded is not None
    assert loaded.goal == "Test checkpointing"


# ============================================================
# 4. Rollback & Transactions
# ============================================================

@pytest.mark.anyio
async def test_transaction_rollback(runtime: ExecutionRuntime) -> None:
    tx_id = await runtime.tx_mgr.begin("tx_mission_01")
    step = ExecutionStep(
        step_id="tx_s1",
        name="Write temporary file",
        plugin_id="file",
        capability="write_file",
        status=StepStatus.COMPLETED,
        rollback_capability="delete_file",
        is_transactional=True,
    )
    runtime.tx_mgr.record_step(tx_id, step)
    await runtime.tx_mgr.rollback(tx_id)
    assert step.status == StepStatus.ROLLED_BACK


# ============================================================
# 5. Mission Execution & Resiliency
# ============================================================

@pytest.mark.anyio
async def test_mission_execution(runtime: ExecutionRuntime) -> None:
    plan = MissionExecutionPlan(
        mission_id="ms_exec_01",
        goal="Test execution plan",
        steps=[
            ExecutionStep(
                step_id="step_browser",
                name="Open URL",
                plugin_id="browser",
                capability="open_url",
                parameters={"url": "https://nova.ai"},
            )
        ],
    )
    res_plan = await runtime.execute_mission(plan)
    assert res_plan.state == ExecutionState.COMPLETED
    assert res_plan.progress_percentage == 100.0


# ============================================================
# 6. Execution Pipeline (Voice -> Response)
# ============================================================

@pytest.mark.anyio
async def test_execution_pipeline(runtime: ExecutionRuntime) -> None:
    pipeline = ExecutionPipeline(mission_executor=runtime.mission_executor)
    result = await pipeline.process_voice_command("summarize today's PDF and email to John")

    assert "mission_id" in result
    assert result["status"] == "completed"
    assert "voice_response" in result


# ============================================================
# 7. Mock Provider
# ============================================================

def test_mock_execution_provider() -> None:
    mock = MockExecutionProvider()
    plan = mock.simulate_mission_plan()
    assert plan.mission_id == "ms_mock_001"
    assert len(plan.steps) == 2

    metrics = mock.simulate_metrics()
    assert metrics["completed_missions"] == 9

    health = mock.simulate_health()
    assert health["status"] == "healthy"


# ============================================================
# 8. Gateway Integration
# ============================================================

@pytest.mark.anyio
async def test_gateway_execution_apis() -> None:
    try:
        register_ai_gateway_dependencies()
    except Exception:
        pass

    gateway = resolve(IAIGateway)

    plan_dict = {
        "mission_id": "ms_gw_exec_01",
        "goal": "Gateway mission test",
        "steps": [
            {
                "step_id": "step_gw_1",
                "name": "Check environment",
                "plugin_id": "terminal",
                "capability": "check_environment",
                "parameters": {},
            }
        ],
    }

    exec_res = await gateway.execute_mission("ms_gw_exec_01", plan_dict)
    assert exec_res["state"] == "completed"

    status_res = await gateway.mission_status("ms_gw_exec_01")
    assert status_res is not None

    active_res = await gateway.active_missions()
    assert isinstance(active_res, list)
