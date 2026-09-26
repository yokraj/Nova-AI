"""Phase 10C Test Suite — Native Task Graph + Cognitive Execution Engine.

Tests:
1. Linear DAG A -> B -> C
2. Branch + merge A -> B / A -> C / B+C -> D
3. Conditional ON_SUCCESS / ON_FAILURE
4. State transition validation
5. Bounded retry
6. Failure propagation
7. Security block
8. Step budget exhaustion
9. Time budget exhaustion
10. Cycle detection
11. WorldState pre/post refresh
12. WorkingMemory synchronization
13. Serialization round trip
14. Real BlenderApplicationAdapter integration
15. Real WindowTracker observation integration
"""

import time
import pytest

from app.ai.desktop_automation.models import AutomationAction
from app.ai.desktop_automation.window_tracker import WindowTracker
from app.ai.desktop_automation.world_state import WorldStateEngine, ProvenanceSource
from app.ai.memory.working_memory import WorkingMemoryManager
from app.ai.kernel.task_graph import (
    DependencyJoinType,
    EdgeCondition,
    GraphValidationError,
    InvalidStateTransitionError,
    NodeState,
    NodeType,
    TaskEdge,
    TaskGraph,
    TaskGraphBuilder,
    TaskGraphExecutor,
    TaskGraphStatus,
    TaskNode,
)


class TestCognitiveTaskGraph:
    """Test suite covering TaskGraph models, state machine, execution, security, and verification."""

    @pytest.mark.asyncio
    async def test_1_linear_dag_execution(self):
        """1. Linear DAG A -> B -> C sequential execution."""
        node_a = TaskNode(node_id="A", title="Step A", node_type=NodeType.OBSERVE)
        node_b = TaskNode(node_id="B", title="Step B", node_type=NodeType.OBSERVE)
        node_c = TaskNode(node_id="C", title="Step C", node_type=NodeType.OBSERVE)

        graph = TaskGraphBuilder.build_linear_graph("task_linear_1", [node_a, node_b, node_c])
        executor = TaskGraphExecutor()

        res = await executor.execute(graph, "Linear Goal")

        assert res.status == TaskGraphStatus.SUCCESS
        assert res.succeeded_nodes_count == 3
        assert node_a.state == NodeState.SUCCEEDED
        assert node_b.state == NodeState.SUCCEEDED
        assert node_c.state == NodeState.SUCCEEDED

    @pytest.mark.asyncio
    async def test_2_branch_and_merge_dag(self):
        """2. Branch + merge DAG: A -> B, A -> C, B+C -> D."""
        graph = TaskGraph(task_id="task_branch_2")
        node_a = TaskNode(node_id="A", title="Root A", node_type=NodeType.OBSERVE)
        node_b = TaskNode(node_id="B", title="Branch B", node_type=NodeType.OBSERVE)
        node_c = TaskNode(node_id="C", title="Branch C", node_type=NodeType.OBSERVE)
        node_d = TaskNode(node_id="D", title="Join D", node_type=NodeType.OBSERVE, join_type=DependencyJoinType.AND)

        graph.add_node(node_a)
        graph.add_node(node_b)
        graph.add_node(node_c)
        graph.add_node(node_d)

        graph.add_edge(TaskEdge("e1", "A", "B"))
        graph.add_edge(TaskEdge("e2", "A", "C"))
        graph.add_edge(TaskEdge("e3", "B", "D"))
        graph.add_edge(TaskEdge("e4", "C", "D"))

        executor = TaskGraphExecutor()
        res = await executor.execute(graph, "Branch Goal")

        assert res.status == TaskGraphStatus.SUCCESS
        assert res.succeeded_nodes_count == 4
        assert node_d.state == NodeState.SUCCEEDED

    @pytest.mark.asyncio
    async def test_3_conditional_edges(self):
        """3. Conditional ON_SUCCESS and ON_FAILURE branch execution."""
        graph = TaskGraph(task_id="task_cond_3")
        node_a = TaskNode(node_id="A", title="Root A", node_type=NodeType.OBSERVE)
        node_success = TaskNode(node_id="B_success", title="Success Handler", node_type=NodeType.OBSERVE)
        node_fail = TaskNode(node_id="C_fail", title="Fail Handler", node_type=NodeType.OBSERVE)

        graph.add_node(node_a)
        graph.add_node(node_success)
        graph.add_node(node_fail)

        graph.add_edge(TaskEdge("e_succ", "A", "B_success", condition=EdgeCondition.ON_SUCCESS))
        graph.add_edge(TaskEdge("e_fail", "A", "C_fail", condition=EdgeCondition.ON_FAILURE))

        executor = TaskGraphExecutor()
        res = await executor.execute(graph, "Conditional Goal")

        assert res.status == TaskGraphStatus.SUCCESS
        assert node_a.state == NodeState.SUCCEEDED
        assert node_success.state == NodeState.SUCCEEDED
        assert node_fail.state == NodeState.SKIPPED

    def test_4_state_transition_validation(self):
        """4. Validates state machine invariants and raises on illegal transitions."""
        node = TaskNode(node_id="N1", title="Test Node")
        assert node.state == NodeState.PENDING

        node.transition_to(NodeState.READY, "Valid ready")
        assert node.state == NodeState.READY

        node.transition_to(NodeState.RUNNING, "Valid running")
        assert node.state == NodeState.RUNNING

        node.transition_to(NodeState.SUCCEEDED, "Valid succeeded")
        assert node.state == NodeState.SUCCEEDED

        # Attempt illegal transition from terminal state SUCCEEDED -> RUNNING
        with pytest.raises(InvalidStateTransitionError):
            node.transition_to(NodeState.RUNNING, "Illegal transition")

    @pytest.mark.asyncio
    async def test_5_bounded_retry(self):
        """5. Bounded retry on failed action attempts up to max_retries."""
        action = AutomationAction(action_type="failing_action", target_label="MockApp")
        node = TaskNode(node_id="R1", title="Retry Node", action=action, max_retries=3)

        graph = TaskGraph(task_id="task_retry_5")
        graph.add_node(node)

        executor = TaskGraphExecutor()
        res = await executor.execute(graph, "Retry Goal")

        assert res.status == TaskGraphStatus.FAILED
        assert node.state == NodeState.FAILED
        assert node.retry_count == 3
        assert len(node.attempt_history) == 3

    @pytest.mark.asyncio
    async def test_6_failure_propagation(self):
        """6. Failure propagation marking downstream nodes BLOCKED/SKIPPED."""
        action = AutomationAction(action_type="failing_action", target_label="MockApp")
        node_a = TaskNode(node_id="A", title="Failing A", action=action, max_retries=1)
        node_b = TaskNode(node_id="B", title="Downstream B", node_type=NodeType.OBSERVE)

        graph = TaskGraph(task_id="task_failprop_6")
        graph.add_node(node_a)
        graph.add_node(node_b)
        graph.add_edge(TaskEdge("e1", "A", "B", condition=EdgeCondition.ON_SUCCESS))

        executor = TaskGraphExecutor()
        res = await executor.execute(graph, "Failure Prop Goal")

        assert res.status == TaskGraphStatus.FAILED
        assert node_a.state == NodeState.FAILED
        assert node_b.state == NodeState.SKIPPED

    @pytest.mark.asyncio
    async def test_7_security_block(self):
        """7. SecurityEngine rejection transitions node to BLOCKED."""
        forbidden_action = AutomationAction(
            action_type="eval",
            target_label="MockApp",
            selector={"code": "__import__('os').system('calc')"},
        )
        node = TaskNode(node_id="SEC1", title="Forbidden Node", action=forbidden_action)

        graph = TaskGraph(task_id="task_sec_7")
        graph.add_node(node)

        executor = TaskGraphExecutor()
        res = await executor.execute(graph, "Security Goal")

        assert res.status == TaskGraphStatus.BLOCKED
        assert node.state == NodeState.BLOCKED
        assert node.failure_category == "SECURITY_BLOCK"

    @pytest.mark.asyncio
    async def test_8_step_budget_exhaustion(self):
        """8. Step budget exhaustion halts execution cleanly."""
        wm_manager = WorkingMemoryManager.get_instance()
        wm_task = wm_manager.create_task("task_budget_8", "Budget Goal")
        wm_task.max_steps = 2

        action = AutomationAction(action_type="failing_action", target_label="MockApp")
        node_a = TaskNode(node_id="A", title="Node A", action=action, max_retries=5)

        graph = TaskGraph(task_id="task_budget_8")
        graph.add_node(node_a)

        executor = TaskGraphExecutor()
        res = await executor.execute(graph, "Budget Goal")

        assert res.status == TaskGraphStatus.BUDGET_EXHAUSTED
        assert "Max steps" in res.error_message

    @pytest.mark.asyncio
    async def test_9_time_budget_exhaustion(self):
        """9. Time budget exhaustion terminates execution."""
        wm_manager = WorkingMemoryManager.get_instance()
        wm_task = wm_manager.create_task("task_time_9", "Time Goal")
        wm_task.time_budget_sec = 0.001  # Immediate timeout
        time.sleep(0.005)

        node_a = TaskNode(node_id="A", title="Node A", node_type=NodeType.OBSERVE)

        graph = TaskGraph(task_id="task_time_9")
        graph.add_node(node_a)

        executor = TaskGraphExecutor()
        res = await executor.execute(graph, "Time Goal")

        assert res.status == TaskGraphStatus.BUDGET_EXHAUSTED
        assert "Time budget" in res.error_message

    def test_10_cycle_detection(self):
        """10. Rejects circular DAG dependencies with GraphValidationError."""
        graph = TaskGraph(task_id="task_cycle_10")
        node_a = TaskNode(node_id="A", title="Node A")
        node_b = TaskNode(node_id="B", title="Node B")

        graph.add_node(node_a)
        graph.add_node(node_b)

        graph.add_edge(TaskEdge("e1", "A", "B"))
        graph.add_edge(TaskEdge("e2", "B", "A"))  # Cycle

        with pytest.raises(GraphValidationError):
            graph.validate()

    @pytest.mark.asyncio
    async def test_11_world_state_pre_post_refresh(self):
        """11. WorldState pre/post execution snapshot hooks."""
        engine = WorldStateEngine.get_instance()
        engine.refresh()

        node_a = TaskNode(node_id="A", title="Obs Node", node_type=NodeType.OBSERVE)
        graph = TaskGraph(task_id="task_ws_11")
        graph.add_node(node_a)

        executor = TaskGraphExecutor()
        res = await executor.execute(graph, "WorldState Goal")

        assert res.status == TaskGraphStatus.SUCCESS
        assert "observed_state" in node_a.metadata

    @pytest.mark.asyncio
    async def test_12_working_memory_synchronization(self):
        """12. Synchronization of node transitions with WorkingMemoryTask."""
        task_id = "task_wm_12"
        node_a = TaskNode(node_id="A", title="Step A", node_type=NodeType.OBSERVE)

        graph = TaskGraph(task_id=task_id)
        graph.add_node(node_a)

        executor = TaskGraphExecutor()
        res = await executor.execute(graph, "WorkingMemory Goal")

        assert res.status == TaskGraphStatus.SUCCESS
        wm = WorkingMemoryManager.get_instance().get_task(task_id)
        assert wm is not None
        assert "A" in wm.completed_nodes

    def test_13_serialization_round_trip(self):
        """13. Lossless TaskGraph serialization and deserialization."""
        graph = TaskGraph(task_id="task_ser_13")
        node_a = TaskNode(node_id="A", title="Node A", node_type=NodeType.OBSERVE)
        node_b = TaskNode(node_id="B", title="Node B", node_type=NodeType.OBSERVE)

        graph.add_node(node_a)
        graph.add_node(node_b)
        graph.add_edge(TaskEdge("e1", "A", "B", condition=EdgeCondition.ON_SUCCESS))

        data = graph.to_dict()
        restored = TaskGraph.from_dict(data)

        assert restored.graph_id == graph.graph_id
        assert restored.task_id == graph.task_id
        assert len(restored.nodes) == 2
        assert len(restored.edges) == 1
        assert restored.nodes["A"].title == "Node A"
        assert restored.edges["e1"].condition == EdgeCondition.ON_SUCCESS

    @pytest.mark.asyncio
    async def test_14_real_blender_application_adapter_integration(self):
        """14. Real structured action execution through BlenderApplicationAdapter & TaskGraph."""
        action = AutomationAction(
            action_type="create_scene",
            target_label="Blender",
            selector={"scene_name": "TaskGraphScene"},
        )
        node = TaskNode(node_id="B1", title="Blender Scene Node", action=action)

        graph = TaskGraph(task_id="task_blender_14")
        graph.add_node(node)

        executor = TaskGraphExecutor()
        res = await executor.execute(graph, "Blender Goal")

        assert res.status == TaskGraphStatus.SUCCESS
        assert node.state == NodeState.SUCCEEDED
        assert node.result is not None
        assert node.result.success is True

    @pytest.mark.asyncio
    async def test_15_real_window_tracker_observation_integration(self):
        """15. Real WindowTracker integration capturing environment observations."""
        tracker = WindowTracker()
        tracker.get_active_window()

        node = TaskNode(node_id="W1", title="Observe Window", node_type=NodeType.OBSERVE)
        graph = TaskGraph(task_id="task_win_15")
        graph.add_node(node)

        executor = TaskGraphExecutor()
        res = await executor.execute(graph, "Window Observation Goal")

        assert res.status == TaskGraphStatus.SUCCESS
        snapshot = WorldStateEngine.get_instance().refresh()
        assert snapshot.windows.foreground_window.source == ProvenanceSource.WINDOW_TRACKER
