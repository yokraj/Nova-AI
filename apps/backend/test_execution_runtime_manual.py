"""Manual validation script for M3.3.10 – Autonomous Skill Execution Runtime & Real-World Automation.

Run from apps/backend/:
    python test_execution_runtime_manual.py

Expected output:
    =========================================
    Nova AI Execution Runtime Validation
    =========================================
    Stage 1  Execution Configuration     PASS
    Stage 2  Context & Data Sharing      PASS
    Stage 3  State Transitions           PASS
    Stage 4  Prioritized Queue           PASS
    Stage 5  Checkpoint Serialization    PASS
    Stage 6  Rollback & Transactions     PASS
    Stage 7  Step Execution & Plugins    PASS
    Stage 8  Human Approval Delegation   PASS
    Stage 9  End-to-End Pipeline         PASS
    Stage 10 Resource & Progress Monitor PASS
    Stage 11 Gateway Integration         PASS
    Stage 12 Complete                    PASS

    12/12 PASS

    Execution Runtime Healthy
"""

import asyncio
import sys


def _banner() -> None:
    print("=========================================")
    print("Nova AI Execution Runtime Validation")
    print("=========================================")


def _result(stage: int, label: str, passed: bool, error: str = "") -> bool:
    status = "PASS" if passed else "FAIL"
    print(f"Stage {stage:<2} {label:<30} {status}")
    if not passed and error:
        print(f"       Error: {error}")
    return passed


def stage_1_configuration() -> bool:
    try:
        from app.ai.execution.configuration import ExecutionConfiguration
        cfg = ExecutionConfiguration()
        assert cfg.max_concurrent_missions == 5
        assert cfg.enable_transactions is True
        return True
    except Exception as e:
        return _result(1, "Execution Configuration", False, str(e)) or False


def stage_2_context() -> bool:
    try:
        from app.ai.execution.execution_context import ExecutionContext
        ctx = ExecutionContext("val_ms")
        ctx.set("key", "val")
        ctx.record_step_output("s1", "out1")
        assert ctx.get("key") == "val"
        assert ctx.get_step_output("s1") == "out1"
        return True
    except Exception as e:
        return _result(2, "Context & Data Sharing", False, str(e)) or False


def stage_3_state() -> bool:
    try:
        from app.ai.execution.state_manager import StateManager
        from app.ai.execution.models import ExecutionState
        sm = StateManager()
        nxt = sm.transition_mission(ExecutionState.PENDING, ExecutionState.RUNNING)
        assert nxt == ExecutionState.RUNNING
        return True
    except Exception as e:
        return _result(3, "State Transitions", False, str(e)) or False


def stage_4_queue() -> bool:
    try:
        from app.ai.execution.execution_queue import ExecutionQueue
        from app.ai.execution.models import MissionExecutionPlan, PriorityLevel
        q = ExecutionQueue(max_concurrent=2)
        q.enqueue(MissionExecutionPlan(mission_id="m1", goal="g1", priority=PriorityLevel.LOW))
        q.enqueue(MissionExecutionPlan(mission_id="m2", goal="g2", priority=PriorityLevel.HIGH))

        deq = q.dequeue()
        assert deq is not None
        assert deq.mission_id == "m2"
        return True
    except Exception as e:
        return _result(4, "Prioritized Queue", False, str(e)) or False


async def stage_5_checkpoint() -> bool:
    try:
        from app.ai.execution.checkpoint_manager import CheckpointManager
        from app.ai.execution.models import MissionExecutionPlan
        cm = CheckpointManager()
        plan = MissionExecutionPlan(mission_id="val_chk_1", goal="val goal")
        await cm.create_checkpoint(plan, {"k": "v"})

        loaded = await cm.load_checkpoint("val_chk_1")
        assert loaded is not None
        assert loaded.goal == "val goal"
        return True
    except Exception as e:
        return _result(5, "Checkpoint Serialization", False, str(e)) or False


async def stage_6_rollback() -> bool:
    try:
        from app.ai.execution.transaction_manager import TransactionManager
        from app.ai.execution.models import ExecutionStep, StepStatus
        tm = TransactionManager()
        tx_id = await tm.begin("m_tx_val")
        step = ExecutionStep(
            step_id="s1", name="step1", plugin_id="file", capability="write_file",
            status=StepStatus.COMPLETED, rollback_capability="delete_file", is_transactional=True
        )
        tm.record_step(tx_id, step)
        await tm.rollback(tx_id)
        assert step.status == StepStatus.ROLLED_BACK
        return True
    except Exception as e:
        return _result(6, "Rollback & Transactions", False, str(e)) or False


async def stage_7_execution() -> bool:
    try:
        from app.ai.execution.execution_runtime import ExecutionRuntime
        from app.ai.execution.models import MissionExecutionPlan, ExecutionStep
        runtime = ExecutionRuntime()
        plan = MissionExecutionPlan(
            mission_id="ms_val_exec",
            goal="Test execution",
            steps=[
                ExecutionStep(step_id="s1", name="Open URL", plugin_id="browser", capability="open_url", parameters={"url": "https://nova.ai"})
            ]
        )
        res = await runtime.execute_mission(plan)
        assert res.state.value == "completed"
        return True
    except Exception as e:
        return _result(7, "Step Execution & Plugins", False, str(e)) or False


async def stage_8_approval() -> bool:
    try:
        from app.ai.execution.approval_handler import ApprovalHandler
        from app.ai.execution.models import ExecutionStep
        ah = ApprovalHandler()
        step = ExecutionStep(step_id="s1", name="Delete file", plugin_id="file", capability="delete_file", requires_approval=True)
        approved = await ah.verify_approval("ms_app_1", step)
        assert approved is True
        return True
    except Exception as e:
        return _result(8, "Human Approval Delegation", False, str(e)) or False


async def stage_9_pipeline() -> bool:
    try:
        from app.ai.execution.execution_runtime import ExecutionRuntime
        runtime = ExecutionRuntime()
        res = await runtime.process_voice_command("summarize today's PDF and email to John")
        assert res["status"] == "completed"
        assert "voice_response" in res
        return True
    except Exception as e:
        return _result(9, "End-to-End Pipeline", False, str(e)) or False


def stage_10_monitoring() -> bool:
    try:
        from app.ai.execution.progress_tracker import ProgressTracker
        from app.ai.execution.resource_manager import ResourceManager
        from app.ai.execution.models import MissionExecutionPlan

        pt = ProgressTracker()
        plan = MissionExecutionPlan(mission_id="m1", goal="g1")
        progress = pt.calculate_progress(plan)
        assert progress >= 0.0

        rm = ResourceManager()
        snap = rm.capture_snapshot()
        assert snap.cpu_percent >= 0.0
        return True
    except Exception as e:
        return _result(10, "Resource & Progress Monitor", False, str(e)) or False


async def stage_11_gateway() -> bool:
    try:
        from app.core.dependency_container import resolve, register_ai_gateway_dependencies
        from app.ai.gateway import IAIGateway

        try:
            register_ai_gateway_dependencies()
        except Exception:
            pass

        gateway = resolve(IAIGateway)
        plan_dict = {
            "mission_id": "ms_gw_val_01",
            "goal": "Gateway validation",
            "steps": [
                {"step_id": "s1", "name": "Check Env", "plugin_id": "terminal", "capability": "check_environment", "parameters": {}}
            ]
        }
        res = await gateway.execute_mission("ms_gw_val_01", plan_dict)
        assert res["state"] == "completed"
        return True
    except Exception as e:
        return _result(11, "Gateway Integration", False, str(e)) or False


async def stage_12_complete() -> bool:
    try:
        from app.ai.execution.mock_provider import MockExecutionProvider
        mock = MockExecutionProvider()
        plan = mock.simulate_mission_plan()
        assert plan.mission_id == "ms_mock_001"

        health = mock.simulate_health()
        assert health["status"] == "healthy"
        return True
    except Exception as e:
        return _result(12, "Complete", False, str(e)) or False


async def main() -> None:
    _banner()

    results = []

    # Sync stages
    results.append(_result(1, "Execution Configuration", stage_1_configuration()))
    results.append(_result(2, "Context & Data Sharing", stage_2_context()))
    results.append(_result(3, "State Transitions", stage_3_state()))
    results.append(_result(4, "Prioritized Queue", stage_4_queue()))

    # Async stages
    results.append(_result(5, "Checkpoint Serialization", await stage_5_checkpoint()))
    results.append(_result(6, "Rollback & Transactions", await stage_6_rollback()))
    results.append(_result(7, "Step Execution & Plugins", await stage_7_execution()))
    results.append(_result(8, "Human Approval Delegation", await stage_8_approval()))
    results.append(_result(9, "End-to-End Pipeline", await stage_9_pipeline()))
    results.append(_result(10, "Resource & Progress Monitor", stage_10_monitoring()))
    results.append(_result(11, "Gateway Integration", await stage_11_gateway()))
    results.append(_result(12, "Complete", await stage_12_complete()))

    passed = sum(results)
    total = len(results)

    print()
    print(f"{passed}/{total} PASS")
    print()

    if passed == total:
        print("Execution Runtime Healthy")
    else:
        print("Execution Runtime Degraded")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
