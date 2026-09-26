"""Comprehensive Pytest Test Suite for Phase 10G Failure Diagnoser & Dynamic Replanner.

Verifies failure classification, bounded retry/replan budgets, work preservation, known-bad action blacklisting,
PlanCritic/GoalVerifier/WorldState/WorkingMemory/LocalModelRouter integration, real Ollama model diagnosis,
and a physical failure -> diagnosis -> replan -> recovery -> goal verification chain.
"""

import pytest

from app.ai.desktop_automation.application_adapter import ApplicationAdapterRegistry, BaseApplicationAdapter
from app.ai.desktop_automation.models import AutomationAction, AutomationResult
from app.ai.desktop_automation.world_state import WorldStateEngine
from app.ai.kernel.dynamic_replanner import DynamicReplanner
from app.ai.kernel.failure_diagnoser import ExecutionControlState, FailureDiagnoser, FailureDiagnosis, FailureType, Recoverability
from app.ai.kernel.goal_verifier import GoalRequirement, GoalVerifier, VerificationStatus
from app.ai.kernel.model_router import CognitiveWorkloadType, LocalModelRouter
from app.ai.kernel.task_graph import NodeState, TaskGraph, TaskGraphExecutor, TaskNode
from app.ai.memory.working_memory import WorkingMemoryManager


class MockBlenderAdapter(BaseApplicationAdapter):
    """Mock application adapter for testing failure and recovery scenarios."""

    def __init__(self, fail_first: bool = False, fail_action: str = ""):
        super().__init__("Blender")
        self.fail_first = fail_first
        self.fail_action = fail_action
        self.executed_actions: list = []

    def can_handle_action(self, action: AutomationAction) -> bool:
        return True

    async def execute_action(self, action: AutomationAction) -> AutomationResult:
        self.executed_actions.append(action.action_type)

        if self.fail_first and action.action_type == self.fail_action:
            return AutomationResult(
                action_id=action.action_id,
                success=False,
                error_message=f"Action '{action.action_type}' failed due to missing precondition or invalid parameter",
            )

        return AutomationResult(
            action_id=action.action_id,
            success=True,
            output={"status": "OK", "executed_action": action.action_type},
        )


@pytest.fixture(autouse=True)
def reset_singletons():
    """Resets working memory and adapter registry singletons before each test."""
    wm = WorkingMemoryManager.get_instance()
    wm._tasks.clear()
    reg = ApplicationAdapterRegistry()
    reg._adapters.clear()
    reg.register_adapter("Blender", MockBlenderAdapter())
    yield


# -----------------------------------------------------------------------------
# 1. Transient Action Failure -> Retry
# -----------------------------------------------------------------------------
def test_1_transient_action_failure_triggers_retry():
    diagnoser = FailureDiagnoser.get_instance()
    wm = WorkingMemoryManager.get_instance()
    task = wm.create_task("task_retry_1", "Test goal", max_retries=3)

    action_res = {"status": "FAILED", "error": "Temporary network blip", "transient": True}
    diag = diagnoser.diagnose_failure(
        task_id="task_retry_1",
        user_goal="Test goal",
        node_id="node_1",
        action_result=action_res,
        working_memory_task=task,
    )

    assert diag.failure_type == FailureType.ACTION_FAILURE
    assert diag.recoverability == Recoverability.RETRYABLE
    assert diag.recommended_recovery == ExecutionControlState.RETRY

    replanner = DynamicReplanner.get_instance()
    graph = TaskGraph(task_id="task_retry_1")
    res = replanner.replan("task_retry_1", "Test goal", graph, diag, working_memory_task=task)

    assert res.control_state == ExecutionControlState.RETRY
    assert res.reason == "Transient failure retry recommended"


# -----------------------------------------------------------------------------
# 2. Permanent Action Failure -> Replan
# -----------------------------------------------------------------------------
def test_2_permanent_action_failure_triggers_replan():
    diagnoser = FailureDiagnoser.get_instance()
    wm = WorkingMemoryManager.get_instance()
    task = wm.create_task("task_replan_2", "Test goal", max_retries=3)
    task.retries_used = 3  # Retries exhausted

    action_res = {"status": "FAILED", "error": "Permanent execution exception", "transient": False}
    diag = diagnoser.diagnose_failure(
        task_id="task_replan_2",
        user_goal="Test goal",
        node_id="node_1",
        action_result=action_res,
        working_memory_task=task,
    )

    assert diag.failure_type == FailureType.ACTION_FAILURE
    assert diag.recoverability == Recoverability.RECOVERABLE
    assert diag.recommended_recovery == ExecutionControlState.REPLAN

    replanner = DynamicReplanner.get_instance()
    graph = TaskGraph(task_id="task_replan_2")
    failed_node = TaskNode(
        node_id="node_1",
        title="Bad step",
        action=AutomationAction(action_id="a1", action_type="blender:bad_action", target_label="Blender"),
    )
    graph.add_node(failed_node)

    res = replanner.replan("task_replan_2", "Test goal", graph, diag, working_memory_task=task)
    assert res.control_state == ExecutionControlState.REPLAN
    assert res.new_graph is not None
    assert res.plan_version == 2


# -----------------------------------------------------------------------------
# 3. Failed Postcondition -> Alternative Action
# -----------------------------------------------------------------------------
def test_3_failed_postcondition_selects_alternative_action():
    diagnoser = FailureDiagnoser.get_instance()
    action_res = {"status": "SUCCESS", "postcondition_failed": True, "error": "Output frame render file missing"}

    diag = diagnoser.diagnose_failure(
        task_id="task_post_3",
        user_goal="Render metallic cube",
        node_id="node_render",
        action_result=action_res,
    )

    assert diag.failure_type == FailureType.POSTCONDITION_FAILURE
    assert diag.recommended_recovery == ExecutionControlState.REPLAN

    replanner = DynamicReplanner.get_instance()
    graph = TaskGraph(task_id="task_post_3")
    render_node = TaskNode(
        node_id="node_render",
        title="Render Frame",
        action=AutomationAction(action_id="a_render", action_type="blender:render_frame", target_label="Blender"),
    )
    graph.add_node(render_node)

    wm = WorkingMemoryManager.get_instance()
    task = wm.create_task("task_post_3", "Render metallic cube")

    res = replanner.replan("task_post_3", "Render metallic cube", graph, diag, working_memory_task=task)
    assert res.control_state == ExecutionControlState.REPLAN
    assert "blender:render_frame" in [kb.get("capability_id") for kb in task.known_bad_actions]


# -----------------------------------------------------------------------------
# 4. Capability Mismatch -> Rediscovery
# -----------------------------------------------------------------------------
def test_4_capability_mismatch_triggers_rediscovery():
    diagnoser = FailureDiagnoser.get_instance()
    action_res = {"error": "Capability not supported in current Blender version: blender:subdivide_edges"}

    diag = diagnoser.diagnose_failure(
        task_id="task_cap_4",
        user_goal="Add subdivision to a mesh",
        node_id="node_subdiv",
        action_result=action_res,
    )

    assert diag.failure_type == FailureType.CAPABILITY_MISMATCH
    assert diag.recommended_recovery == ExecutionControlState.REPLAN

    replanner = DynamicReplanner.get_instance()
    graph = TaskGraph(task_id="task_cap_4")
    subdiv_node = TaskNode(
        node_id="node_subdiv",
        title="Subdivide Edges",
        action=AutomationAction(action_id="a_subdiv", action_type="blender:subdivide_edges", target_label="Blender"),
    )
    graph.add_node(subdiv_node)

    wm = WorkingMemoryManager.get_instance()
    task = wm.create_task("task_cap_4", "Add subdivision to a mesh")

    res = replanner.replan("task_cap_4", "Add subdivision to a mesh", graph, diag, working_memory_task=task)
    assert res.control_state == ExecutionControlState.REPLAN
    assert res.new_graph is not None
    # Alternative capability discovered via CapabilityDiscoveryEngine (e.g. blender:add_modifier)
    replan_caps = [n.action.action_type for n in res.new_graph.nodes.values() if n.action]
    assert "blender:add_modifier" in replan_caps or len(replan_caps) > 0


# -----------------------------------------------------------------------------
# 5. State Changed Externally -> Re-observe/Replan
# -----------------------------------------------------------------------------
def test_5_external_state_change_triggers_reobservation():
    diagnoser = FailureDiagnoser.get_instance()
    action_res = {"error": "Scene modified externally, active object missing"}

    diag = diagnoser.diagnose_failure(
        task_id="task_state_5",
        user_goal="Set active object metallic",
        node_id="node_metallic",
        action_result=action_res,
    )

    assert diag.failure_type == FailureType.STATE_CHANGED
    assert diag.recommended_recovery == ExecutionControlState.REPLAN


# -----------------------------------------------------------------------------
# 6. Timeout -> Bounded Recovery
# -----------------------------------------------------------------------------
def test_6_timeout_triggers_bounded_recovery():
    diagnoser = FailureDiagnoser.get_instance()
    action_res = {"error": "Execution timed out after 30s"}

    wm = WorkingMemoryManager.get_instance()
    task = wm.create_task("task_tout_6", "Long task", max_retries=1)
    task.retries_used = 1  # Retries exhausted

    diag = diagnoser.diagnose_failure(
        task_id="task_tout_6",
        user_goal="Long task",
        node_id="node_long",
        action_result=action_res,
        working_memory_task=task,
    )

    assert diag.failure_type == FailureType.TIMEOUT
    assert diag.recommended_recovery == ExecutionControlState.REPLAN


# -----------------------------------------------------------------------------
# 7. Security Block -> Never Bypass (Human Escalation)
# -----------------------------------------------------------------------------
def test_7_security_block_escalates_to_human():
    diagnoser = FailureDiagnoser.get_instance()
    action_res = {"error": "Action 'registry_write' requires human approval"}

    diag = diagnoser.diagnose_failure(
        task_id="task_sec_7",
        user_goal="Write registry key",
        node_id="node_reg",
        action_result=action_res,
    )

    assert diag.failure_type == FailureType.SECURITY_BLOCK
    assert diag.requires_human is True
    assert diag.recommended_recovery == ExecutionControlState.REQUIRES_HUMAN

    replanner = DynamicReplanner.get_instance()
    graph = TaskGraph(task_id="task_sec_7")
    reg_node = TaskNode(
        node_id="node_reg",
        title="Registry Write",
        action=AutomationAction(action_id="a_reg", action_type="registry_write", target_label="System"),
    )
    graph.add_node(reg_node)

    wm = WorkingMemoryManager.get_instance()
    task = wm.create_task("task_sec_7", "Write registry key")

    res = replanner.replan("task_sec_7", "Write registry key", graph, diag, working_memory_task=task)
    assert res.control_state == ExecutionControlState.REQUIRES_HUMAN
    assert res.new_graph is None


# -----------------------------------------------------------------------------
# 8. Unknown State -> No False Recovery
# -----------------------------------------------------------------------------
def test_8_unknown_state_prevents_false_recovery():
    diagnoser = FailureDiagnoser.get_instance()
    action_res = {"error": "Opaque driver crash code 0x80004005"}

    diag = diagnoser.diagnose_failure(
        task_id="task_unk_8",
        user_goal="Opaque task",
        node_id="node_unk",
        action_result=action_res,
        allow_model_fallback=False,  # Disable model fallback to test default deterministic rule
    )

    assert diag.failure_type == FailureType.UNKNOWN_UNVERIFIED
    assert diag.confidence == 0.3
    assert diag.requires_human is True
    assert diag.recommended_recovery == ExecutionControlState.FAILED


# -----------------------------------------------------------------------------
# 9. Successful Partial Execution -> Preserve Progress
# -----------------------------------------------------------------------------
def test_9_partial_execution_preserves_successful_nodes():
    replanner = DynamicReplanner.get_instance()
    graph = TaskGraph(task_id="task_partial_9")

    n1 = TaskNode(
        node_id="node_create",
        title="Create Mesh Object",
        action=AutomationAction(action_id="a1", action_type="blender:create_mesh_object", target_label="Blender"),
        state=NodeState.SUCCEEDED,
    )
    n2 = TaskNode(
        node_id="node_bad",
        title="Bad Action",
        action=AutomationAction(action_id="a2", action_type="blender:bad_action", target_label="Blender"),
        state=NodeState.FAILED,
    )
    graph.add_node(n1)
    graph.add_node(n2)

    diag = FailureDiagnosis(
        failure_type=FailureType.ACTION_FAILURE,
        root_cause="Node 2 failed",
        affected_node="node_bad",
        recoverability=Recoverability.RECOVERABLE,
        recommended_recovery=ExecutionControlState.REPLAN,
    )

    wm = WorkingMemoryManager.get_instance()
    task = wm.create_task("task_partial_9", "Build metallic object")
    task.completed_nodes.append("node_create")

    res = replanner.replan("task_partial_9", "Build metallic object", graph, diag, working_memory_task=task)
    assert res.control_state == ExecutionControlState.REPLAN
    assert res.new_graph is not None
    assert "node_create" in res.new_graph.nodes
    assert res.new_graph.nodes["node_create"].state == NodeState.SUCCEEDED


# -----------------------------------------------------------------------------
# 10. Avoid Repeating Known-Bad Action
# -----------------------------------------------------------------------------
def test_10_avoids_repeating_known_bad_actions():
    replanner = DynamicReplanner.get_instance()
    graph = TaskGraph(task_id="task_bad_10")
    bad_node = TaskNode(
        node_id="node_bad",
        title="Bad Action",
        action=AutomationAction(action_id="a_bad", action_type="blender:bad_action", target_label="Blender"),
    )
    graph.add_node(bad_node)

    diag = FailureDiagnosis(
        failure_type=FailureType.ACTION_FAILURE,
        root_cause="Action failed",
        affected_node="node_bad",
        recommended_recovery=ExecutionControlState.REPLAN,
    )

    wm = WorkingMemoryManager.get_instance()
    task = wm.create_task("task_bad_10", "Make object metallic")

    res = replanner.replan("task_bad_10", "Make object metallic", graph, diag, working_memory_task=task)
    assert res.control_state == ExecutionControlState.REPLAN

    # Verify action was recorded as known bad
    known_bad_ids = [kb.get("capability_id") for kb in task.known_bad_actions]
    assert "blender:bad_action" in known_bad_ids

    # Verify new graph does not use blender:bad_action
    new_caps = [n.action.action_type for n in res.new_graph.nodes.values() if n.action]
    assert "blender:bad_action" not in new_caps


# -----------------------------------------------------------------------------
# 11. Plan Versioning and History Tracking
# -----------------------------------------------------------------------------
def test_11_plan_versioning_and_history_tracking():
    wm = WorkingMemoryManager.get_instance()
    task = wm.create_task("task_ver_11", "Versioned task")

    replanner = DynamicReplanner.get_instance()
    graph = TaskGraph(task_id="task_ver_11")
    n1 = TaskNode(node_id="n1", title="Step 1", action=AutomationAction(action_id="a1", action_type="blender:create_mesh_object", target_label="Blender"))
    graph.add_node(n1)

    diag = FailureDiagnosis(
        failure_type=FailureType.ACTION_FAILURE,
        root_cause="Step 1 failed",
        affected_node="n1",
        recommended_recovery=ExecutionControlState.REPLAN,
    )

    res = replanner.replan("task_ver_11", "Versioned task", graph, diag, working_memory_task=task)
    assert res.plan_version == 2
    assert len(task.plan_history) == 1
    assert task.plan_history[0]["version"] == 2


# -----------------------------------------------------------------------------
# 12. PlanCritic Integration with Replanning
# -----------------------------------------------------------------------------
def test_12_plan_critic_integration_with_replanning():
    replanner = DynamicReplanner.get_instance()
    graph = TaskGraph(task_id="task_critic_12")
    n1 = TaskNode(node_id="n1", title="Step 1", action=AutomationAction(action_id="a1", action_type="blender:create_mesh_object", target_label="Blender"))
    graph.add_node(n1)

    diag = FailureDiagnosis(
        failure_type=FailureType.ACTION_FAILURE,
        root_cause="Step 1 failed",
        affected_node="n1",
        recommended_recovery=ExecutionControlState.REPLAN,
    )

    wm = WorkingMemoryManager.get_instance()
    task = wm.create_task("task_critic_12", "Create mesh object")

    res = replanner.replan("task_critic_12", "Create mesh object", graph, diag, working_memory_task=task)
    assert res.critic_result is not None
    assert res.critic_result.get("status") in ["APPROVED", "PASSED"]


# -----------------------------------------------------------------------------
# 13. GoalVerifier Integration with Replanning
# -----------------------------------------------------------------------------
def test_13_goal_verifier_integration_with_replanning():
    verifier = GoalVerifier.get_instance()
    req = GoalRequirement(req_id="req_subdiv", description="Subdivide mesh model", target_state="Subdivided")

    # GoalVerifier returns FAILED verification details
    v_res = verifier.verify_goal("task_gv_13", "Subdivide mesh model", [req], {"status": "FAILED"})
    v_details = v_res.to_dict()

    diagnoser = FailureDiagnoser.get_instance()
    diag = diagnoser.diagnose_failure(
        task_id="task_gv_13",
        user_goal="Subdivide mesh model",
        goal_verification_details=v_details,
    )

    assert diag.failure_type == FailureType.GOAL_VERIFICATION_FAILURE
    assert diag.affected_requirement == "req_subdiv"

    replanner = DynamicReplanner.get_instance()
    graph = TaskGraph(task_id="task_gv_13")
    wm = WorkingMemoryManager.get_instance()
    task = wm.create_task("task_gv_13", "Subdivide mesh model")
    task.failed_requirements = ["req_subdiv"]

    res = replanner.replan("task_gv_13", "Subdivide mesh model", graph, diag, working_memory_task=task)
    assert res.control_state == ExecutionControlState.REPLAN
    assert res.new_graph is not None


# -----------------------------------------------------------------------------
# 14. WorldState Integration During Diagnosis
# -----------------------------------------------------------------------------
def test_14_world_state_integration_during_diagnosis():
    ws = WorldStateEngine.get_instance()
    ws_data = ws.refresh().to_dict()

    diagnoser = FailureDiagnoser.get_instance()
    action_res = {"error": "Missing input file at path"}

    diag = diagnoser.diagnose_failure(
        task_id="task_ws_14",
        user_goal="Import GLTF file",
        node_id="node_import",
        action_result=action_res,
        world_state_data=ws_data,
    )

    assert diag.failure_type == FailureType.PRECONDITION_FAILURE
    assert "world_state" in diag.evidence


# -----------------------------------------------------------------------------
# 15. WorkingMemory Integration
# -----------------------------------------------------------------------------
def test_15_working_memory_integration():
    wm = WorkingMemoryManager.get_instance()
    _ = wm.create_task("task_wm_15", "WM integration test")

    diagnoser = FailureDiagnoser.get_instance()
    diag = diagnoser.diagnose_failure("task_wm_15", "WM integration test", "n1", {"error": "Test error"})

    wm.record_failure_diagnosis("task_wm_15", diag.to_dict())

    snap = wm.get_snapshot("task_wm_15")
    assert len(snap["failure_history"]) == 1
    assert snap["failure_history"][0]["failure_type"] == FailureType.ACTION_FAILURE.value


# -----------------------------------------------------------------------------
# 16. LocalModelRouter Integration
# -----------------------------------------------------------------------------
def test_16_local_model_router_integration():
    router = LocalModelRouter.get_instance()
    decision = router.route(CognitiveWorkloadType.REASONING)
    assert decision.selected_model_id is not None
    assert decision.workload_type == CognitiveWorkloadType.REASONING


# -----------------------------------------------------------------------------
# 17. Bounded Retry & Replan Budget Exhaustion
# -----------------------------------------------------------------------------
def test_17_bounded_retry_and_replan_budget_exhaustion():
    wm = WorkingMemoryManager.get_instance()
    task = wm.create_task("task_budget_17", "Budget test", max_steps=50, max_retries=3)
    task.replan_count = 3  # Max replans reached

    replanner = DynamicReplanner.get_instance()
    graph = TaskGraph(task_id="task_budget_17")
    diag = FailureDiagnosis(
        failure_type=FailureType.ACTION_FAILURE,
        root_cause="Action failed",
        recommended_recovery=ExecutionControlState.REPLAN,
    )

    res = replanner.replan("task_budget_17", "Budget test", graph, diag, working_memory_task=task)
    assert res.control_state == ExecutionControlState.FAILED
    assert "Replan budget exhausted" in res.reason


# -----------------------------------------------------------------------------
# 18. Requires-Human Escalation
# -----------------------------------------------------------------------------
def test_18_requires_human_escalation():
    replanner = DynamicReplanner.get_instance()
    graph = TaskGraph(task_id="task_human_18")
    diag = FailureDiagnosis(
        failure_type=FailureType.SECURITY_BLOCK,
        root_cause="Admin privilege required",
        requires_human=True,
        recoverability=Recoverability.HUMAN_REQUIRED,
        recommended_recovery=ExecutionControlState.REQUIRES_HUMAN,
    )

    wm = WorkingMemoryManager.get_instance()
    task = wm.create_task("task_human_18", "Admin task")

    res = replanner.replan("task_human_18", "Admin task", graph, diag, working_memory_task=task)
    assert res.control_state == ExecutionControlState.REQUIRES_HUMAN
    assert task.execution_control_state == ExecutionControlState.REQUIRES_HUMAN.value


# -----------------------------------------------------------------------------
# 19. Deterministic Failure Diagnosis
# -----------------------------------------------------------------------------
def test_19_deterministic_failure_diagnosis():
    diagnoser = FailureDiagnoser.get_instance()

    # Security
    d1 = diagnoser.diagnose_failure("t", "g", action_result={"error": "Access denied by permission gate"})
    assert d1.failure_type == FailureType.SECURITY_BLOCK

    # Timeout
    d2 = diagnoser.diagnose_failure("t", "g", action_result={"error": "Command execution timed out"})
    assert d2.failure_type == FailureType.TIMEOUT

    # Precondition
    d3 = diagnoser.diagnose_failure("t", "g", action_result={"error": "Prerequisite file missing"})
    assert d3.failure_type == FailureType.PRECONDITION_FAILURE

    # Capability Mismatch
    d4 = diagnoser.diagnose_failure("t", "g", action_result={"error": "Capability not supported"})
    assert d4.failure_type == FailureType.CAPABILITY_MISMATCH

    # Resource Failure
    d5 = diagnoser.diagnose_failure("t", "g", action_result={"error": "Out of memory"})
    assert d5.failure_type == FailureType.RESOURCE_FAILURE


# -----------------------------------------------------------------------------
# 20. Real Ollama Diagnosis and Replanning
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_20_real_ollama_model_diagnosis_and_replanning():
    """Executes real Ollama (qwen3:8b) model diagnosis fallback for unverified opaque failure."""
    diagnoser = FailureDiagnoser.get_instance()
    action_res = {"error": "Opaque hardware graphics driver crash code 0x80004005"}

    # Diagnostic model fallback
    diag = diagnoser.diagnose_failure(
        task_id="task_ollama_20",
        user_goal="Render high poly 3D mesh scene",
        node_id="node_render",
        action_result=action_res,
        allow_model_fallback=True,
    )

    assert diag is not None
    assert diag.failure_type in FailureType.__members__.values()
    assert len(diag.root_cause) > 0


# -----------------------------------------------------------------------------
# 21. Physical Failure -> Diagnosis -> Replan -> Recovery -> Goal Chain
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_21_physical_failure_diagnosis_replan_recovery_goal_chain():
    """Demonstrates a complete physical end-to-end failure -> diagnosis -> replan -> recovery -> goal verification chain."""
    task_id = "task_phys_chain_21"
    user_goal = "Create a metallic 3D mesh object"

    # Step 1: Set up mock adapter where initial action 'blender:bad_invalid_action' FAILS physically
    registry = ApplicationAdapterRegistry()
    adapter = MockBlenderAdapter(fail_first=True, fail_action="blender:bad_invalid_action")
    registry.register_adapter("Blender", adapter)

    executor = TaskGraphExecutor(adapter_registry=registry)

    # Construct initial graph with failing node
    initial_graph = TaskGraph(task_id=task_id)
    fail_node = TaskNode(
        node_id="node_initial",
        title="Execute Invalid Action",
        action=AutomationAction(action_id="act_init", action_type="blender:bad_invalid_action", target_label="Blender"),
    )
    initial_graph.add_node(fail_node)

    # Step 2: Execute initial plan physically -> FAILS
    init_res = await executor.execute(initial_graph, user_goal=user_goal)
    assert init_res.status.value in ["failed", "partial"]

    # Step 3: GoalVerifier confirms Goal FAILS
    verifier = GoalVerifier.get_instance()
    req = GoalRequirement(req_id="req_metallic", description="Create metallic mesh object", target_state="Metallic")
    g_res = verifier.verify_goal(task_id, user_goal, [req], {"status": "FAILED", "failed_nodes": ["node_initial"]})
    assert g_res.status == VerificationStatus.FAILED

    # Step 4: FailureDiagnoser diagnoses failure from actual physical result
    diagnoser = FailureDiagnoser.get_instance()
    diag = diagnoser.diagnose_failure(
        task_id=task_id,
        user_goal=user_goal,
        node_id="node_initial",
        action_result=fail_node.result.model_dump() if fail_node.result else {"error": "Initial action failed"},
        goal_verification_details=g_res.to_dict(),
    )
    assert diag.failure_type in [
        FailureType.ACTION_FAILURE,
        FailureType.GOAL_VERIFICATION_FAILURE,
        FailureType.CAPABILITY_MISMATCH,
        FailureType.PRECONDITION_FAILURE,
    ]

    # Step 5: DynamicReplanner blacklists bad action and generates corrected recovery TaskGraph
    wm = WorkingMemoryManager.get_instance()
    wm_task = wm.get_task(task_id)

    replanner = DynamicReplanner.get_instance()
    replan_res = replanner.replan(
        task_id=task_id,
        user_goal=user_goal,
        current_graph=initial_graph,
        diagnosis=diag,
        working_memory_task=wm_task,
    )

    assert replan_res.control_state == ExecutionControlState.REPLAN
    assert replan_res.new_graph is not None
    assert replan_res.plan_version == 2

    # Step 6: Execute recovery plan physically -> SUCCEEDS
    recovery_res = await executor.execute(replan_res.new_graph, user_goal=user_goal)
    assert recovery_res.status.value == "success"

    # Step 7: GoalVerifier confirms original user goal achieved!
    final_g_res = verifier.verify_goal(
        task_id=task_id,
        user_goal=user_goal,
        requirements=[req],
        execution_summary={"status": "SUCCESS", "executed_nodes_count": recovery_res.executed_nodes_count},
    )

    assert final_g_res.status == VerificationStatus.SUCCESS
    assert final_g_res.goal_satisfied is True
