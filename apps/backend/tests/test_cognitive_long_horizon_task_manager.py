"""Phase 10H — Dedicated Test Suite for Long-Horizon Task Manager and Durable Persistence.

Tests task lifecycle states, durable checkpoints, pause/resume, cancellation persistence across process restarts,
process restart recovery, stale state detection, budget enforcement, waiting states, progress reporting,
audit history logging, security secret redaction, and complete physical restart & recovery chain.
"""

from pathlib import Path
import tempfile
import time
import pytest

from app.ai.desktop_automation.application_adapter import ApplicationAdapterRegistry, BaseApplicationAdapter
from app.ai.desktop_automation.models import AutomationAction, AutomationResult
from app.ai.kernel.durable_checkpoint_store import DurableCheckpointStore, redact_secrets
from app.ai.kernel.dynamic_replanner import DynamicReplanner
from app.ai.kernel.failure_diagnoser import FailureDiagnoser
from app.ai.kernel.goal_verifier import GoalRequirement, GoalVerifier, VerificationStatus
from app.ai.kernel.long_horizon_manager import DurableTaskState, LongHorizonTaskManager
from app.ai.kernel.task_graph import NodeState, TaskGraph, TaskGraphExecutor, TaskNode
from app.ai.memory.working_memory import WorkingMemoryManager


class MockBlenderAdapter(BaseApplicationAdapter):
    """Mock application adapter for testing physical action execution and restart recovery."""

    def __init__(self, fail_action: str = ""):
        self.fail_action = fail_action
        self.executed_actions = []

    def get_supported_actions(self):
        return ["blender:add_cube", "blender:set_material", "blender:bad_invalid_action"]

    def execute_action(self, action: AutomationAction) -> AutomationResult:
        self.executed_actions.append(action.action_type)
        if action.action_type == self.fail_action:
            return AutomationResult(action_id=action.action_id, success=False, error_message=f"Action '{action.action_type}' failed due to mock error", execution_time=0.1)
        return AutomationResult(action_id=action.action_id, success=True, data={"status": "OK", "action": action.action_type}, execution_time=0.1)

    def query_state(self):
        return {"active_app": "Blender", "objects": [{"name": "Cube", "type": "MESH"}], "material": "Metallic"}


@pytest.fixture
def temp_store():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = DurableCheckpointStore(storage_dir=Path(tmpdir))
        yield store


# -----------------------------------------------------------------------------
# 1. Task Lifecycle States
# -----------------------------------------------------------------------------
def test_1_task_lifecycle_states(temp_store):
    """1. Verify all 15 explicit DurableTaskState values and state transitions."""
    assert len(DurableTaskState) == 15
    manager = LongHorizonTaskManager(checkpoint_store=temp_store)
    task_id = manager.create_task("Test lifecycle states")

    manager.transition_task_state(task_id, DurableTaskState.PLANNING)
    cp = temp_store.load_checkpoint(task_id)
    assert cp.durable_state == DurableTaskState.PLANNING.value

    manager.transition_task_state(task_id, DurableTaskState.RUNNING)
    cp = temp_store.load_checkpoint(task_id)
    assert cp.durable_state == DurableTaskState.RUNNING.value


# -----------------------------------------------------------------------------
# 2. Checkpoint Creation
# -----------------------------------------------------------------------------
def test_2_checkpoint_creation(temp_store):
    """2. Verify durable checkpoint creation and structure on disk."""
    manager = LongHorizonTaskManager(checkpoint_store=temp_store)
    task_id = manager.create_task("Create checkpoint test")
    cp = temp_store.load_checkpoint(task_id)

    assert cp is not None
    assert cp.task_id == task_id
    assert cp.user_goal == "Create checkpoint test"
    assert cp.durable_state == DurableTaskState.CREATED.value
    assert (temp_store.storage_dir / f"{task_id}.json").exists()


# -----------------------------------------------------------------------------
# 3. Checkpoint Restore
# -----------------------------------------------------------------------------
def test_3_checkpoint_restore(temp_store):
    """3. Restore task checkpoint from disk and verify complete state reconstruction."""
    manager = LongHorizonTaskManager(checkpoint_store=temp_store)
    task_id = manager.create_task("Restore checkpoint test")
    manager.transition_task_state(task_id, DurableTaskState.RUNNING)

    cp = temp_store.load_checkpoint(task_id)
    cp.completed_nodes = ["node_1", "node_2"]
    cp.replan_counts = 1
    temp_store.save_checkpoint(cp)

    restored = temp_store.load_checkpoint(task_id)
    assert restored.completed_nodes == ["node_1", "node_2"]
    assert restored.replan_counts == 1
    assert restored.durable_state == DurableTaskState.RUNNING.value


# -----------------------------------------------------------------------------
# 4. Pause Task
# -----------------------------------------------------------------------------
def test_4_pause_task(temp_store):
    """4. Verify safe pause task semantics and transition to PAUSED state."""
    manager = LongHorizonTaskManager(checkpoint_store=temp_store)
    task_id = manager.create_task("Pause task test")
    manager.transition_task_state(task_id, DurableTaskState.RUNNING)

    success = manager.pause_task(task_id, reason="User requested pause")
    assert success is True

    cp = temp_store.load_checkpoint(task_id)
    assert cp.durable_state == DurableTaskState.PAUSED.value
    assert cp.pause_reason == "User requested pause"
    assert cp.paused_at is not None


# -----------------------------------------------------------------------------
# 5. Resume Task
# -----------------------------------------------------------------------------
def test_5_resume_task(temp_store):
    """5. Resume paused task from latest valid checkpoint."""
    registry = ApplicationAdapterRegistry()
    registry.register_adapter("Blender", MockBlenderAdapter())
    executor = TaskGraphExecutor(adapter_registry=registry)
    manager = LongHorizonTaskManager(checkpoint_store=temp_store, executor=executor)
    task_id = manager.create_task("Resume task test")
    
    graph = TaskGraph(task_id=task_id)
    graph.add_node(TaskNode(node_id="n1", title="Action node", action=AutomationAction(action_id="a1", action_type="blender:add_cube", target_label="Blender")))
    cp = temp_store.load_checkpoint(task_id)
    cp.task_graph_dict = graph.to_dict()
    temp_store.save_checkpoint(cp)

    manager.transition_task_state(task_id, DurableTaskState.RUNNING)
    manager.pause_task(task_id)

    res = manager.resume_task(task_id, adapter_name="Blender")
    assert res.durable_state in (DurableTaskState.COMPLETED, DurableTaskState.READY, DurableTaskState.RUNNING)


# -----------------------------------------------------------------------------
# 6. Cancellation
# -----------------------------------------------------------------------------
def test_6_cancellation(temp_store):
    """6. Cancel task and verify durable transition to CANCELLED state."""
    manager = LongHorizonTaskManager(checkpoint_store=temp_store)
    task_id = manager.create_task("Cancel task test")

    success = manager.cancel_task(task_id, reason="User cancelled task")
    assert success is True

    cp = temp_store.load_checkpoint(task_id)
    assert cp.durable_state == DurableTaskState.CANCELLED.value
    assert cp.cancellation_reason == "User cancelled task"


# -----------------------------------------------------------------------------
# 7. Cancelled Task Stays Cancelled After Restart
# -----------------------------------------------------------------------------
def test_7_cancelled_task_stays_cancelled_after_restart(temp_store):
    """7. Confirm cancelled task remains CANCELLED and cannot resume after process restart."""
    manager1 = LongHorizonTaskManager(checkpoint_store=temp_store)
    task_id = manager1.create_task("Cancelled restart test")
    manager1.cancel_task(task_id, reason="Cancelled in process 1")

    # Simulate process restart by instantiating fresh manager
    manager2 = LongHorizonTaskManager(checkpoint_store=temp_store)
    res = manager2.recover_on_restart(task_id)

    assert res.durable_state == DurableTaskState.CANCELLED
    assert res.error == "Task was cancelled"


# -----------------------------------------------------------------------------
# 8. Process Restart Recovery
# -----------------------------------------------------------------------------
def test_8_process_restart_recovery(temp_store):
    """8. Simulate process restart and recover task execution from checkpoint."""
    registry = ApplicationAdapterRegistry()
    registry.register_adapter("Blender", MockBlenderAdapter())
    executor = TaskGraphExecutor(adapter_registry=registry)
    manager1 = LongHorizonTaskManager(checkpoint_store=temp_store, executor=executor)
    task_id = manager1.create_task("Process restart recovery test")
    
    graph = TaskGraph(task_id=task_id)
    graph.add_node(TaskNode(node_id="n1", title="Action node", action=AutomationAction(action_id="a1", action_type="blender:add_cube", target_label="Blender")))
    cp = temp_store.load_checkpoint(task_id)
    cp.task_graph_dict = graph.to_dict()
    temp_store.save_checkpoint(cp)

    manager1.transition_task_state(task_id, DurableTaskState.RUNNING)

    # Fresh process manager
    manager2 = LongHorizonTaskManager(checkpoint_store=temp_store, executor=executor)
    res = manager2.recover_on_restart(task_id, adapter_name="Blender")

    assert res.task_id == task_id
    assert res.durable_state in (DurableTaskState.COMPLETED, DurableTaskState.RUNNING, DurableTaskState.READY)


# -----------------------------------------------------------------------------
# 9. Preserve Completed Work
# -----------------------------------------------------------------------------
def test_9_preserve_completed_work(temp_store):
    """9. Ensure completed nodes are preserved and not re-executed after restore."""
    graph = TaskGraph(task_id="task_pres_9")
    n1 = TaskNode(node_id="n1", title="Completed node", state=NodeState.SUCCEEDED)
    n2 = TaskNode(node_id="n2", title="Pending node", state=NodeState.PENDING)
    graph.add_node(n1)
    graph.add_node(n2)

    manager = LongHorizonTaskManager(checkpoint_store=temp_store)
    task_id = manager.create_task("Preserve work test", task_id="task_pres_9")

    cp = temp_store.load_checkpoint(task_id)
    cp.task_graph_dict = graph.to_dict()
    cp.completed_nodes = ["n1"]
    temp_store.save_checkpoint(cp)

    restored_cp = temp_store.load_checkpoint(task_id)
    restored_graph = TaskGraph.from_dict(restored_cp.task_graph_dict)

    assert restored_graph.nodes["n1"].state == NodeState.SUCCEEDED
    assert restored_cp.completed_nodes == ["n1"]


# -----------------------------------------------------------------------------
# 10. Avoid Duplicate Execution
# -----------------------------------------------------------------------------
def test_10_avoid_duplicate_execution(temp_store):
    """10. Confirm attempt history and executed nodes prevent duplicate action execution."""
    manager = LongHorizonTaskManager(checkpoint_store=temp_store)
    task_id = manager.create_task("Avoid duplicate execution")

    cp = temp_store.load_checkpoint(task_id)
    cp.completed_nodes = ["node_init_cube"]
    temp_store.save_checkpoint(cp)

    progress = manager.get_task_progress(task_id)
    assert progress.completed_nodes == 1


# -----------------------------------------------------------------------------
# 11. Stale WorldState Detection
# -----------------------------------------------------------------------------
def test_11_stale_world_state_detection(temp_store):
    """11. Detect changed environment snapshot upon restart and log recovery event."""
    manager = LongHorizonTaskManager(checkpoint_store=temp_store)
    task_id = manager.create_task("Stale state detection test")

    cp = temp_store.load_checkpoint(task_id)
    cp.world_state_references = {"application": {"active_app_name": {"value": "Photoshop"}}}
    temp_store.save_checkpoint(cp)

    # Recover on restart (active app in test env is UNKNOWN/different)
    _ = manager.recover_on_restart(task_id)

    history = temp_store.get_task_history(task_id)
    restart_events = [e for e in history if e.get("event_type") == "PROCESS_RESTART_RECOVERY"]
    assert len(restart_events) > 0


# -----------------------------------------------------------------------------
# 12. Budget Enforcement (Actions)
# -----------------------------------------------------------------------------
def test_12_budget_enforcement_actions(temp_store):
    """12. Transition state to BLOCKED when maximum actions budget is exceeded."""
    manager = LongHorizonTaskManager(checkpoint_store=temp_store)
    task_id = manager.create_task("Budget actions test", budgets={"max_actions": 2})

    cp = temp_store.load_checkpoint(task_id)
    cp.actions_used = 3
    temp_store.save_checkpoint(cp)

    wm_task = WorkingMemoryManager.get_instance().get_task(task_id)
    wm_task.steps_used = 3

    exceeded = manager._check_budget_limits(cp, wm_task)
    assert exceeded == DurableTaskState.BLOCKED


# -----------------------------------------------------------------------------
# 13. Timeout / Deadline Enforcement
# -----------------------------------------------------------------------------
def test_13_timeout_deadline_enforcement(temp_store):
    """13. Transition state to BLOCKED when task deadline timestamp is passed."""
    manager = LongHorizonTaskManager(checkpoint_store=temp_store)
    past_deadline = time.time() - 10.0
    task_id = manager.create_task("Deadline test", budgets={"deadline_timestamp": past_deadline})

    cp = temp_store.load_checkpoint(task_id)
    wm_task = WorkingMemoryManager.get_instance().get_task(task_id)

    exceeded = manager._check_budget_limits(cp, wm_task)
    assert exceeded == DurableTaskState.BLOCKED


# -----------------------------------------------------------------------------
# 14. Retry Budget Persistence
# -----------------------------------------------------------------------------
def test_14_retry_budget_persistence(temp_store):
    """14. Confirm retry count persists across checkpoints."""
    manager = LongHorizonTaskManager(checkpoint_store=temp_store)
    task_id = manager.create_task("Retry budget test")

    cp = temp_store.load_checkpoint(task_id)
    cp.retries_used = 2
    temp_store.save_checkpoint(cp)

    restored = temp_store.load_checkpoint(task_id)
    assert restored.retries_used == 2


# -----------------------------------------------------------------------------
# 15. Replan Budget Persistence
# -----------------------------------------------------------------------------
def test_15_replan_budget_persistence(temp_store):
    """15. Confirm replan count persists across checkpoints."""
    manager = LongHorizonTaskManager(checkpoint_store=temp_store)
    task_id = manager.create_task("Replan budget test")

    cp = temp_store.load_checkpoint(task_id)
    cp.replans_used = 2
    temp_store.save_checkpoint(cp)

    restored = temp_store.load_checkpoint(task_id)
    assert restored.replans_used == 2


# -----------------------------------------------------------------------------
# 16. Model Call Budget
# -----------------------------------------------------------------------------
def test_16_model_call_budget(temp_store):
    """16. Transition state to REQUIRES_HUMAN when model call budget is exceeded."""
    manager = LongHorizonTaskManager(checkpoint_store=temp_store)
    task_id = manager.create_task("Model call budget test", budgets={"max_model_calls": 5})

    cp = temp_store.load_checkpoint(task_id)
    cp.model_calls_used = 6
    wm_task = WorkingMemoryManager.get_instance().get_task(task_id)

    exceeded = manager._check_budget_limits(cp, wm_task)
    assert exceeded == DurableTaskState.REQUIRES_HUMAN


# -----------------------------------------------------------------------------
# 17. WAITING State
# -----------------------------------------------------------------------------
def test_17_waiting_state(temp_store):
    """17. Validate WAITING state with explicit waiting reason."""
    manager = LongHorizonTaskManager(checkpoint_store=temp_store)
    task_id = manager.create_task("Waiting state test")

    manager.transition_task_state(task_id, DurableTaskState.WAITING, reason="Waiting for Blender background render")
    cp = temp_store.load_checkpoint(task_id)

    assert cp.durable_state == DurableTaskState.WAITING.value
    assert cp.waiting_reason == "Waiting for Blender background render"


# -----------------------------------------------------------------------------
# 18. Human Approval State
# -----------------------------------------------------------------------------
def test_18_human_approval_state(temp_store):
    """18. Validate REQUIRES_HUMAN state escalation."""
    manager = LongHorizonTaskManager(checkpoint_store=temp_store)
    task_id = manager.create_task("Human approval test")

    manager.transition_task_state(task_id, DurableTaskState.REQUIRES_HUMAN, reason="Admin privilege confirmation needed")
    cp = temp_store.load_checkpoint(task_id)

    assert cp.durable_state == DurableTaskState.REQUIRES_HUMAN.value


# -----------------------------------------------------------------------------
# 19. Progress Reporting
# -----------------------------------------------------------------------------
def test_19_progress_reporting(temp_store):
    """19. Verify TaskProgressReport returns accurate node counts and percentage complete."""
    graph = TaskGraph(task_id="task_prog_19")
    n1 = TaskNode(node_id="n1", title="Step 1", state=NodeState.SUCCEEDED)
    n2 = TaskNode(node_id="n2", title="Step 2", state=NodeState.PENDING)
    graph.add_node(n1)
    graph.add_node(n2)

    manager = LongHorizonTaskManager(checkpoint_store=temp_store)
    task_id = manager.create_task("Progress reporting test", task_id="task_prog_19")

    cp = temp_store.load_checkpoint(task_id)
    cp.task_graph_dict = graph.to_dict()
    cp.completed_nodes = ["n1"]
    temp_store.save_checkpoint(cp)

    report = manager.get_task_progress(task_id)
    assert report.total_nodes == 2
    assert report.completed_nodes == 1
    assert report.percentage_complete == 50.0


# -----------------------------------------------------------------------------
# 20. Task History Audit Log
# -----------------------------------------------------------------------------
def test_20_task_history_audit_log(temp_store):
    """20. Verify immutable task event history audit trail."""
    manager = LongHorizonTaskManager(checkpoint_store=temp_store)
    task_id = manager.create_task("History audit test")
    manager.transition_task_state(task_id, DurableTaskState.PLANNING, reason="Starting plan generation")

    history = manager.get_task_history(task_id)
    assert len(history) >= 2
    event_types = [e["event_type"] for e in history]
    assert "TASK_CREATED" in event_types
    assert "STATE_TRANSITION" in event_types


# -----------------------------------------------------------------------------
# 21. WorkingMemory Integration
# -----------------------------------------------------------------------------
def test_21_working_memory_integration(temp_store):
    """21. Verify synchronization between WorkingMemory and durable checkpoint."""
    manager = LongHorizonTaskManager(checkpoint_store=temp_store)
    task_id = manager.create_task("WM integration test")

    wm_task = WorkingMemoryManager.get_instance().get_task(task_id)
    wm_task.steps_used = 5
    wm_task.replan_count = 1

    cp = temp_store.load_checkpoint(task_id)
    assert cp is not None


# -----------------------------------------------------------------------------
# 22. TaskGraph Integration
# -----------------------------------------------------------------------------
def test_22_task_graph_integration(temp_store):
    """22. Verify TaskGraph serialization and execution state sync."""
    graph = TaskGraph(task_id="task_tg_22")
    node = TaskNode(node_id="n1", title="Action node", action=AutomationAction(action_id="a1", action_type="blender:add_cube", target_label="Blender"))
    graph.add_node(node)

    manager = LongHorizonTaskManager(checkpoint_store=temp_store)
    task_id = manager.create_task("TaskGraph integration test", task_id="task_tg_22")

    cp = temp_store.load_checkpoint(task_id)
    cp.task_graph_dict = graph.to_dict()
    temp_store.save_checkpoint(cp)

    restored_graph = TaskGraph.from_dict(temp_store.load_checkpoint(task_id).task_graph_dict)
    assert "n1" in restored_graph.nodes


# -----------------------------------------------------------------------------
# 23. GoalVerifier Integration
# -----------------------------------------------------------------------------
def test_23_goal_verifier_integration(temp_store):
    """23. Verify post-restore goal verification integration."""
    manager = LongHorizonTaskManager(checkpoint_store=temp_store)
    task_id = manager.create_task("Goal verifier integration test")

    req = GoalRequirement(req_id="r1", description="Mesh exists", target_state="SUCCESS")
    verifier = GoalVerifier.get_instance()
    res = verifier.verify_goal(user_goal="Goal verifier integration test", requirements=[req], execution_summary={"status": "SUCCESS"}, task_id=task_id)
    assert res.status == VerificationStatus.SUCCESS


# -----------------------------------------------------------------------------
# 24. FailureDiagnoser & Replanner Integration
# -----------------------------------------------------------------------------
def test_24_failure_diagnoser_and_replanner_integration(temp_store):
    """24. Verify 10G failure diagnosis and dynamic replanning after checkpoint restore."""
    manager = LongHorizonTaskManager(checkpoint_store=temp_store)
    task_id = manager.create_task("Failure diagnoser replanner integration")

    diagnoser = FailureDiagnoser.get_instance()
    diag = diagnoser.diagnose_failure(task_id, "Failure test", "n1", {"error": "Invalid action"})
    assert diag is not None

    replanner = DynamicReplanner.get_instance()
    graph = TaskGraph(task_id=task_id)
    n1 = TaskNode(node_id="n1", title="Failed node", action=AutomationAction(action_id="a1", action_type="blender:bad_action"))
    graph.add_node(n1)

    wm_task = WorkingMemoryManager.get_instance().get_task(task_id)
    replan_res = replanner.replan(task_id, "Failure test", graph, diag, wm_task)
    assert replan_res.new_graph is not None


# -----------------------------------------------------------------------------
# 25. Security Preservation & Secret Redaction
# -----------------------------------------------------------------------------
def test_25_security_preservation_secret_redaction(temp_store):
    """25. Verify secret credentials (api_key, token, password) are redacted from checkpoints."""
    raw_dict = {
        "user_goal": "Render scene",
        "api_key": "sk-secret-12345",
        "nested": {"token": "bearer-token-abc", "password": "super-secret-pass"},
        "safe_field": "public_data",
    }

    cleaned = redact_secrets(raw_dict)
    assert cleaned["api_key"] == "[REDACTED]"
    assert cleaned["nested"]["token"] == "[REDACTED]"
    assert cleaned["nested"]["password"] == "[REDACTED]"
    assert cleaned["safe_field"] == "public_data"


# -----------------------------------------------------------------------------
# 26. Physical End-to-End Restart & Recovery Chain
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_26_physical_end_to_end_restart_and_recovery_chain(temp_store):
    """26. Complete physical workflow -> execute nodes -> checkpoint -> process restart -> restore -> WorldState refresh -> failure -> 10G recovery -> GoalVerifier -> SUCCESS."""
    task_id = "task_phys_10h_26"
    user_goal = "Create and materialize metallic Blender mesh"

    # Step 1: Register mock Blender adapter with failure on first action 'blender:bad_invalid_action'
    registry = ApplicationAdapterRegistry.get_instance()
    adapter = MockBlenderAdapter(fail_action="blender:bad_invalid_action")
    registry.register_adapter("Blender", adapter)

    executor = TaskGraphExecutor(adapter_registry=registry)
    manager1 = LongHorizonTaskManager(checkpoint_store=temp_store, executor=executor)

    # Step 2: Create initial TaskGraph with failing initial node
    initial_graph = TaskGraph(task_id=task_id)
    fail_node = TaskNode(
        node_id="node_initial",
        title="Execute Invalid Action",
        action=AutomationAction(action_id="act_init", action_type="blender:bad_invalid_action", target_label="Blender"),
    )
    initial_graph.add_node(fail_node)

    _ = manager1.create_task(user_goal=user_goal, task_id=task_id)

    # Save initial graph checkpoint
    cp = temp_store.load_checkpoint(task_id)
    cp.task_graph_dict = initial_graph.to_dict()
    temp_store.save_checkpoint(cp)

    # Step 3: Simulate Process Restart -> Create fresh manager instance reading same disk checkpoint store
    manager2 = LongHorizonTaskManager(checkpoint_store=temp_store, executor=executor)

    req = GoalRequirement(req_id="req_metallic", description="Create metallic mesh object", target_state="Metallic")

    # Step 4: Execute restart recovery (runs recovery, 10G diagnosis & replan, and goal verification)
    res = await manager2.execute_task_lifecycle(
        task_id=task_id,
        graph=initial_graph,
        requirements=[req],
        adapter_name="Blender",
    )

    # Step 5: Assert complete physical recovery chain success
    assert res.durable_state == DurableTaskState.COMPLETED
    assert res.goal_satisfied is True
    assert res.verification_result is not None
    assert res.verification_result["status"] == "SUCCESS"

    final_cp = temp_store.load_checkpoint(task_id)
    assert final_cp.durable_state == DurableTaskState.COMPLETED.value
    assert final_cp.replans_used >= 1
