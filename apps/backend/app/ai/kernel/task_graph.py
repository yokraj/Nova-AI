"""Native Task Graph and Cognitive Execution Engine for Nova-AI.

Implements stateful DAG task graphs, node state machines, conditional edge evaluation,
bounded retry loops, WorldState pre/post observation hooks, WorkingMemory synchronization,
SecurityEngine gating, and ApplicationAdapter execution.
"""

from dataclasses import dataclass, field
from enum import Enum
import inspect
import time
from typing import Any, Dict, List, Optional, Set
import uuid

import structlog

from app.ai.desktop_automation.application_adapter import ApplicationAdapterRegistry, BaseApplicationAdapter
from app.ai.desktop_automation.models import AutomationAction, AutomationResult, VerificationResult
from app.ai.desktop_automation.security_engine import SecurityEngine
from app.ai.desktop_automation.verification_engine import VerificationEngine
from app.ai.desktop_automation.world_state import WorldStateEngine
from app.ai.memory.working_memory import WorkingMemoryManager, WorkingMemoryTask

logger = structlog.get_logger("task_graph")


class NodeType(str, Enum):
    """Enumerate task graph node types."""

    GOAL = "goal"
    PLAN = "plan"
    ACTION = "action"
    OBSERVE = "observe"
    VERIFY = "verify"
    DECISION = "decision"
    WAIT = "wait"
    RECOVERY = "recovery"
    COMPLETE = "complete"
    FAIL = "fail"


class NodeState(str, Enum):
    """Enumerate task graph node lifecycle states."""

    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    WAITING = "waiting"
    VERIFYING = "verifying"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


class EdgeCondition(str, Enum):
    """Enumerate task edge conditions."""

    ALWAYS = "always"
    ON_SUCCESS = "on_success"
    ON_FAILURE = "on_failure"
    ON_CONDITION = "on_condition"


class TaskGraphStatus(str, Enum):
    """Enumerate overall graph execution result status."""

    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"
    BUDGET_EXHAUSTED = "budget_exhausted"


class DependencyJoinType(str, Enum):
    """Dependency resolution join semantics for nodes with multiple inputs."""

    AND = "and"
    OR = "or"


class GraphValidationError(Exception):
    """Raised when task graph structure or cycle validation fails."""

    pass


class InvalidStateTransitionError(Exception):
    """Raised when an illegal node state transition is attempted."""

    pass


@dataclass
class TaskEdge:
    """Directional edge connecting source and target nodes with condition rules."""

    edge_id: str
    source_node_id: str
    target_node_id: str
    condition: EdgeCondition = EdgeCondition.ALWAYS
    condition_param: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
            "condition": self.condition.value if isinstance(self.condition, EdgeCondition) else str(self.condition),
            "condition_param": self.condition_param,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskEdge":
        return cls(
            edge_id=data["edge_id"],
            source_node_id=data["source_node_id"],
            target_node_id=data["target_node_id"],
            condition=EdgeCondition(data.get("condition", EdgeCondition.ALWAYS.value)),
            condition_param=data.get("condition_param"),
        )


# Valid state transition mapping
VALID_TRANSITIONS: Dict[NodeState, Set[NodeState]] = {
    NodeState.PENDING: {NodeState.READY, NodeState.SKIPPED, NodeState.BLOCKED, NodeState.CANCELLED},
    NodeState.READY: {NodeState.RUNNING, NodeState.CANCELLED, NodeState.BLOCKED, NodeState.SKIPPED},
    NodeState.RUNNING: {
        NodeState.WAITING,
        NodeState.VERIFYING,
        NodeState.SUCCEEDED,
        NodeState.FAILED,
        NodeState.BLOCKED,
        NodeState.CANCELLED,
    },
    NodeState.WAITING: {NodeState.RUNNING, NodeState.VERIFYING, NodeState.FAILED, NodeState.CANCELLED},
    NodeState.VERIFYING: {
        NodeState.SUCCEEDED,
        NodeState.RUNNING,
        NodeState.READY,
        NodeState.FAILED,
        NodeState.BLOCKED,
        NodeState.CANCELLED,
    },
    NodeState.SUCCEEDED: set(),
    NodeState.FAILED: set(),
    NodeState.SKIPPED: set(),
    NodeState.CANCELLED: set(),
    NodeState.BLOCKED: set(),
}


@dataclass
class TaskNode:
    """Cognitive graph node representing an action, goal, check, or decision step."""

    node_id: str
    title: str
    node_type: NodeType = NodeType.ACTION
    action: Optional[AutomationAction] = None
    expected_state: Optional[str] = None
    state: NodeState = NodeState.PENDING
    result: Optional[AutomationResult] = None
    verification: Optional[VerificationResult] = None
    retry_count: int = 0
    max_retries: int = 3
    attempt_history: List[Dict[str, Any]] = field(default_factory=list)
    failure_reason: Optional[str] = None
    failure_category: Optional[str] = None
    last_error: Optional[str] = None
    recovery_attempts: List[Dict[str, Any]] = field(default_factory=list)
    in_edges: List[str] = field(default_factory=list)
    out_edges: List[str] = field(default_factory=list)
    join_type: DependencyJoinType = DependencyJoinType.AND
    metadata: Dict[str, Any] = field(default_factory=dict)

    def transition_to(self, new_state: NodeState, reason: str = "") -> None:
        """Transitions node to new state, enforcing strict state machine invariants."""
        if self.state == new_state:
            return

        valid_targets = VALID_TRANSITIONS.get(self.state, set())
        if new_state not in valid_targets:
            raise InvalidStateTransitionError(
                f"Invalid transition for node '{self.node_id}' ({self.title}): {self.state.value} -> {new_state.value}. Allowed: {[s.value for s in valid_targets]}"
            )

        logger.debug(
            "Node state transition",
            node_id=self.node_id,
            old_state=self.state.value,
            new_state=new_state.value,
            reason=reason,
        )
        self.state = new_state

    def is_terminal(self) -> bool:
        """Returns True if node is in a terminal state."""
        return self.state in {
            NodeState.SUCCEEDED,
            NodeState.FAILED,
            NodeState.SKIPPED,
            NodeState.CANCELLED,
            NodeState.BLOCKED,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "title": self.title,
            "node_type": self.node_type.value if isinstance(self.node_type, NodeType) else str(self.node_type),
            "action": self.action.model_dump() if self.action and hasattr(self.action, "model_dump") else self.action,
            "expected_state": self.expected_state,
            "state": self.state.value if isinstance(self.state, NodeState) else str(self.state),
            "result": self.result.model_dump() if self.result and hasattr(self.result, "model_dump") else self.result,
            "verification": self.verification.model_dump() if self.verification and hasattr(self.verification, "model_dump") else self.verification,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "attempt_history": self.attempt_history,
            "failure_reason": self.failure_reason,
            "failure_category": self.failure_category,
            "last_error": self.last_error,
            "recovery_attempts": self.recovery_attempts,
            "in_edges": self.in_edges,
            "out_edges": self.out_edges,
            "join_type": self.join_type.value if isinstance(self.join_type, DependencyJoinType) else str(self.join_type),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskNode":
        action_data = data.get("action")
        action_obj = AutomationAction(**action_data) if isinstance(action_data, dict) else action_data

        res_data = data.get("result")
        res_obj = AutomationResult(**res_data) if isinstance(res_data, dict) else res_data

        ver_data = data.get("verification")
        ver_obj = VerificationResult(**ver_data) if isinstance(ver_data, dict) else ver_data

        return cls(
            node_id=data["node_id"],
            title=data["title"],
            node_type=NodeType(data.get("node_type", NodeType.ACTION.value)),
            action=action_obj,
            expected_state=data.get("expected_state"),
            state=NodeState(data.get("state", NodeState.PENDING.value)),
            result=res_obj,
            verification=ver_obj,
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3),
            attempt_history=data.get("attempt_history", []),
            failure_reason=data.get("failure_reason"),
            failure_category=data.get("failure_category"),
            last_error=data.get("last_error"),
            recovery_attempts=data.get("recovery_attempts", []),
            in_edges=data.get("in_edges", []),
            out_edges=data.get("out_edges", []),
            join_type=DependencyJoinType(data.get("join_type", DependencyJoinType.AND.value)),
            metadata=data.get("metadata", {}),
        )


@dataclass
class TaskGraph:
    """Stateful Cognitive DAG Task Graph holding nodes and condition edges."""

    graph_id: str = field(default_factory=lambda: f"graph_{uuid.uuid4().hex[:8]}")
    task_id: str = field(default_factory=lambda: f"task_{uuid.uuid4().hex[:8]}")
    nodes: Dict[str, TaskNode] = field(default_factory=dict)
    edges: Dict[str, TaskEdge] = field(default_factory=dict)
    root_node_id: Optional[str] = None
    terminal_node_ids: List[str] = field(default_factory=list)

    def add_node(self, node: TaskNode) -> None:
        """Adds a node to the graph."""
        self.nodes[node.node_id] = node
        if not self.root_node_id:
            self.root_node_id = node.node_id

    def add_edge(self, edge: TaskEdge) -> None:
        """Adds a directional edge connecting source and target nodes."""
        if edge.source_node_id not in self.nodes:
            raise GraphValidationError(f"Source node '{edge.source_node_id}' does not exist in graph.")
        if edge.target_node_id not in self.nodes:
            raise GraphValidationError(f"Target node '{edge.target_node_id}' does not exist in graph.")

        self.edges[edge.edge_id] = edge
        self.nodes[edge.source_node_id].out_edges.append(edge.edge_id)
        self.nodes[edge.target_node_id].in_edges.append(edge.edge_id)

    def validate(self) -> None:
        """Validates graph structure, checking for cycles and dangling references."""
        if not self.nodes:
            raise GraphValidationError("TaskGraph has no nodes.")

        # Cycle detection using DFS
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def dfs_cycle(nid: str) -> bool:
            visited.add(nid)
            rec_stack.add(nid)

            node = self.nodes[nid]
            for eid in node.out_edges:
                edge = self.edges.get(eid)
                if not edge:
                    continue
                target_id = edge.target_node_id
                if target_id not in visited:
                    if dfs_cycle(target_id):
                        return True
                elif target_id in rec_stack:
                    return True

            rec_stack.discard(nid)
            return False

        for nid in self.nodes:
            if nid not in visited:
                if dfs_cycle(nid):
                    raise GraphValidationError(f"Circular dependency cycle detected at node '{nid}'.")

    def get_ready_nodes(self) -> List[TaskNode]:
        """Computes and returns nodes currently eligible for execution."""
        ready: List[TaskNode] = []

        for node in self.nodes.values():
            if node.state != NodeState.PENDING:
                continue

            if not node.in_edges:
                # No incoming dependencies -> Ready
                ready.append(node)
                continue

            # Evaluate incoming edges
            incoming_statuses: List[bool] = []
            has_blocked_parent = False

            for eid in node.in_edges:
                edge = self.edges.get(eid)
                if not edge:
                    continue
                src_node = self.nodes.get(edge.source_node_id)
                if not src_node:
                    continue

                if src_node.state == NodeState.BLOCKED:
                    has_blocked_parent = True

                # Evaluate edge condition
                satisfied = False
                if edge.condition == EdgeCondition.ALWAYS:
                    satisfied = src_node.state in {NodeState.SUCCEEDED, NodeState.SKIPPED}
                elif edge.condition == EdgeCondition.ON_SUCCESS:
                    satisfied = (src_node.state == NodeState.SUCCEEDED)
                elif edge.condition == EdgeCondition.ON_FAILURE:
                    satisfied = (src_node.state in {NodeState.FAILED, NodeState.BLOCKED})
                elif edge.condition == EdgeCondition.ON_CONDITION:
                    satisfied = (src_node.state == NodeState.SUCCEEDED and src_node.metadata.get("condition_value") == edge.condition_param)

                incoming_statuses.append(satisfied)

            if has_blocked_parent and node.join_type == DependencyJoinType.AND and not any(
                self.edges[eid].condition == EdgeCondition.ON_FAILURE for eid in node.in_edges
            ):
                # Permanent blockage propagation
                node.transition_to(NodeState.BLOCKED, "Upstream parent is BLOCKED")
                continue

            if node.join_type == DependencyJoinType.AND:
                if all(incoming_statuses):
                    ready.append(node)
            elif node.join_type == DependencyJoinType.OR:
                if any(incoming_statuses):
                    ready.append(node)

        return ready

    def to_dict(self) -> Dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "task_id": self.task_id,
            "root_node_id": self.root_node_id,
            "terminal_node_ids": self.terminal_node_ids,
            "nodes": {nid: n.to_dict() for nid, n in self.nodes.items()},
            "edges": {eid: e.to_dict() for eid, e in self.edges.items()},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskGraph":
        graph = cls(
            graph_id=data["graph_id"],
            task_id=data["task_id"],
            root_node_id=data.get("root_node_id"),
            terminal_node_ids=data.get("terminal_node_ids", []),
        )
        for nid, ndata in data.get("nodes", {}).items():
            graph.nodes[nid] = TaskNode.from_dict(ndata)
        for eid, edata in data.get("edges", {}).items():
            graph.edges[eid] = TaskEdge.from_dict(edata)
        return graph


@dataclass
class TaskGraphResult:
    """Payload summarizing the outcome of a TaskGraph execution."""

    graph_id: str
    task_id: str
    status: TaskGraphStatus
    executed_nodes_count: int = 0
    succeeded_nodes_count: int = 0
    failed_nodes_count: int = 0
    blocked_nodes_count: int = 0
    skipped_nodes_count: int = 0
    final_output: Optional[Any] = None
    error_message: Optional[str] = None
    start_time: float = field(default_factory=time.time)
    end_time: float = field(default_factory=time.time)
    duration_sec: float = 0.0


class TaskGraphBuilder:
    """Helper class to construct TaskGraph DAGs programmatically."""

    @staticmethod
    def build_linear_graph(task_id: str, nodes: List[TaskNode]) -> TaskGraph:
        """Constructs a simple sequential linear A -> B -> C graph."""
        graph = TaskGraph(task_id=task_id)
        if not nodes:
            return graph

        prev_node: Optional[TaskNode] = None
        for node in nodes:
            graph.add_node(node)
            if prev_node:
                edge_id = f"edge_{prev_node.node_id}_to_{node.node_id}"
                edge = TaskEdge(
                    edge_id=edge_id,
                    source_node_id=prev_node.node_id,
                    target_node_id=node.node_id,
                    condition=EdgeCondition.ON_SUCCESS,
                )
                graph.add_edge(edge)
            prev_node = node

        if nodes:
            graph.terminal_node_ids = [nodes[-1].node_id]

        graph.validate()
        return graph


class TaskGraphExecutor:
    """Executes TaskGraph DAGs sequentially with security gating, observation, verification, and budget enforcement."""

    def __init__(
        self,
        security_engine: Optional[SecurityEngine] = None,
        adapter_registry: Optional[ApplicationAdapterRegistry] = None,
        verification_engine: Optional[VerificationEngine] = None,
        world_state_engine: Optional[WorldStateEngine] = None,
        working_memory_manager: Optional[WorkingMemoryManager] = None,
    ) -> None:
        self.security_engine = security_engine or SecurityEngine()
        self.adapter_registry = adapter_registry or ApplicationAdapterRegistry()
        self.verification_engine = verification_engine or VerificationEngine()
        self.world_state_engine = world_state_engine or WorldStateEngine.get_instance()
        self.working_memory_manager = working_memory_manager or WorkingMemoryManager.get_instance()

    async def execute(self, graph: TaskGraph, user_goal: str = "TaskGraph Execution") -> TaskGraphResult:
        """Executes the task graph sequentially for ready nodes until completion or budget exhaustion."""
        start_time = time.time()
        logger.info("Starting TaskGraph execution", graph_id=graph.graph_id, task_id=graph.task_id)

        # Validate graph upfront
        graph.validate()

        # Initialize or retrieve WorkingMemoryTask
        wm_task: WorkingMemoryTask = self.working_memory_manager.get_task(graph.task_id) or self.working_memory_manager.create_task(
            task_id=graph.task_id,
            user_goal=user_goal,
        )

        executed_cnt = 0
        succeeded_cnt = 0
        failed_cnt = 0
        blocked_cnt = 0
        skipped_cnt = 0

        # Main execution loop
        while True:
            # 1. Budget Checks
            now = time.time()
            if wm_task.steps_used >= wm_task.max_steps:
                logger.warning("TaskGraph budget exhausted (max_steps reached)", steps=wm_task.steps_used)
                self._cancel_remaining_nodes(graph, "Max steps budget exhausted")
                return self._build_result(
                    graph, TaskGraphStatus.BUDGET_EXHAUSTED, executed_cnt, succeeded_cnt, failed_cnt, blocked_cnt, skipped_cnt, start_time, "Max steps budget exhausted"
                )

            if (now - wm_task.start_time) >= wm_task.time_budget_sec:
                logger.warning("TaskGraph budget exhausted (time_budget reached)", elapsed=now - wm_task.start_time)
                self._cancel_remaining_nodes(graph, "Time budget exhausted")
                return self._build_result(
                    graph, TaskGraphStatus.BUDGET_EXHAUSTED, executed_cnt, succeeded_cnt, failed_cnt, blocked_cnt, skipped_cnt, start_time, "Time budget exhausted"
                )

            # 2. Query Ready Nodes
            ready_nodes = graph.get_ready_nodes()
            if not ready_nodes:
                # Check if all nodes are terminal
                all_terminal = all(n.is_terminal() for n in graph.nodes.values())
                if all_terminal:
                    break

                # Handle pending nodes whose parents have reached terminal states
                resolved_any = False
                for node in list(graph.nodes.values()):
                    if node.state != NodeState.PENDING:
                        continue

                    # Check if all parent nodes are terminal
                    parents = [graph.nodes[graph.edges[eid].source_node_id] for eid in node.in_edges if graph.edges.get(eid) and graph.edges[eid].source_node_id in graph.nodes]
                    if parents and all(p.is_terminal() for p in parents):
                        # Evaluate edge satisfaction
                        edge_statuses = []
                        for eid in node.in_edges:
                            edge = graph.edges.get(eid)
                            if not edge:
                                continue
                            pnode = graph.nodes.get(edge.source_node_id)
                            if not pnode:
                                continue
                            satisfied = False
                            if edge.condition == EdgeCondition.ALWAYS:
                                satisfied = pnode.state in {NodeState.SUCCEEDED, NodeState.SKIPPED}
                            elif edge.condition == EdgeCondition.ON_SUCCESS:
                                satisfied = (pnode.state == NodeState.SUCCEEDED)
                            elif edge.condition == EdgeCondition.ON_FAILURE:
                                satisfied = (pnode.state in {NodeState.FAILED, NodeState.BLOCKED})
                            elif edge.condition == EdgeCondition.ON_CONDITION:
                                satisfied = (pnode.state == NodeState.SUCCEEDED and pnode.metadata.get("condition_value") == edge.condition_param)
                            edge_statuses.append(satisfied)

                        is_ready = (all(edge_statuses) if node.join_type == DependencyJoinType.AND else any(edge_statuses))
                        if is_ready:
                            node.transition_to(NodeState.READY, "Parent terminal state satisfied edge condition")
                            ready_nodes.append(node)
                        else:
                            node.transition_to(NodeState.SKIPPED, "Parent terminal state unsatisfied edge condition")
                            skipped_cnt += 1
                        resolved_any = True

                if not ready_nodes and not resolved_any:
                    break

            if not ready_nodes:
                break

            # Sequential ready node dispatch
            current_node = ready_nodes[0]
            current_node.transition_to(NodeState.READY, "Node eligible for execution")

            # Execute current node
            await self._execute_node(graph, current_node, wm_task)
            executed_cnt += 1

            if current_node.state == NodeState.SUCCEEDED:
                succeeded_cnt += 1
            elif current_node.state == NodeState.FAILED:
                failed_cnt += 1
            elif current_node.state == NodeState.BLOCKED:
                blocked_cnt += 1
            elif current_node.state == NodeState.SKIPPED:
                skipped_cnt += 1

            # Update skipped counts from graph traversal
            for n in graph.nodes.values():
                if n.state == NodeState.SKIPPED and n.metadata.get("counted") is not True:
                    n.metadata["counted"] = True

        # Final Graph Outcome Evaluation
        end_time = time.time()
        final_status = TaskGraphStatus.SUCCESS

        if blocked_cnt > 0 and succeeded_cnt == 0:
            final_status = TaskGraphStatus.BLOCKED
        elif failed_cnt > 0 and succeeded_cnt == 0:
            final_status = TaskGraphStatus.FAILED
        elif failed_cnt > 0 or blocked_cnt > 0:
            final_status = TaskGraphStatus.PARTIAL
        elif succeeded_cnt == 0 and len(graph.nodes) > 0:
            final_status = TaskGraphStatus.FAILED

        wm_task.task_status = "COMPLETED" if final_status == TaskGraphStatus.SUCCESS else "FAILED"

        return TaskGraphResult(
            graph_id=graph.graph_id,
            task_id=graph.task_id,
            status=final_status,
            executed_nodes_count=executed_cnt,
            succeeded_nodes_count=succeeded_cnt,
            failed_nodes_count=failed_cnt,
            blocked_nodes_count=blocked_cnt,
            skipped_nodes_count=skipped_cnt,
            start_time=start_time,
            end_time=end_time,
            duration_sec=round(end_time - start_time, 3),
        )

    async def _execute_node(self, graph: TaskGraph, node: TaskNode, wm_task: WorkingMemoryTask) -> bool:
        """Executes a single node through state transitions, security, adapter, and verification."""
        self.working_memory_manager.set_current_node(graph.task_id, node.node_id)
        node.transition_to(NodeState.RUNNING, "Starting node execution")

        # Non-action nodes (GOAL, DECISION, WAIT, COMPLETE, OBSERVE)
        if node.node_type != NodeType.ACTION or not node.action:
            if node.node_type == NodeType.OBSERVE:
                snapshot = self.world_state_engine.refresh()
                obs_dict = snapshot.to_dict() if hasattr(snapshot, "to_dict") else str(snapshot)
                self.working_memory_manager.record_observation(graph.task_id, {"node_id": node.node_id, "snapshot": obs_dict})
                node.metadata["observed_state"] = obs_dict

            node.transition_to(NodeState.SUCCEEDED, f"Non-action node {node.node_type.value} completed")
            self.working_memory_manager.complete_node(graph.task_id, node.node_id)
            return True

        # Action Node Execution Loop (Supports Bounded Retries)
        action: AutomationAction = node.action

        while True:
            wm_task.steps_used += 1

            # 1. WorldState PRE-execution observation
            pre_snapshot = self.world_state_engine.refresh()
            pre_obs_dict = pre_snapshot.to_dict() if hasattr(pre_snapshot, "to_dict") else str(pre_snapshot)
            self.working_memory_manager.record_observation(graph.task_id, {"node_id": node.node_id, "pre_execution": pre_obs_dict})

            # 2. Security Engine Boundary Gate
            sec_valid = True
            sec_reason = ""
            action_type = getattr(action, "action_type", "") or ""
            selector_str = str(getattr(action, "selector", {}))
            value_str = str(getattr(action, "value", ""))

            if any(term in (action_type + selector_str + value_str) for term in ["eval", "exec", "__import__", "os.system", "subprocess"]):
                sec_valid = False
                sec_reason = f"Forbidden dynamic code execution in action '{action_type}'"
            elif self.security_engine.check_approval_required(action_type):
                sec_valid = False
                sec_reason = f"Action '{action_type}' requires human approval"
            if not sec_valid:
                logger.warning("Action blocked by SecurityEngine", node_id=node.node_id, reason=sec_reason)
                node.transition_to(NodeState.BLOCKED, f"Security rejection: {sec_reason}")
                node.failure_reason = sec_reason
                node.failure_category = "SECURITY_BLOCK"
                self.working_memory_manager.fail_node(graph.task_id, node.node_id, sec_reason)
                return False

            # 3. Application Adapter Execution
            target_app = action.target_label or "Blender"
            adapter: BaseApplicationAdapter = self.adapter_registry.get_adapter(target_app)

            exec_start = time.time()
            action_result: AutomationResult
            try:
                res_obj = None
                if hasattr(adapter, "execute_action"):
                    res_obj = adapter.execute_action(action)
                elif hasattr(adapter, "execute"):
                    res_obj = adapter.execute(action)
                else:
                    res_obj = AutomationResult(
                        action_id=action.action_id,
                        success=False,
                        error_message=f"Adapter {adapter.__class__.__name__} does not support execute_action",
                    )

                if inspect.isawaitable(res_obj):
                    action_result = await res_obj
                else:
                    action_result = res_obj
            except Exception as ex:
                action_result = AutomationResult(
                    action_id=action.action_id,
                    success=False,
                    error_message=f"Adapter execution exception: {str(ex)}",
                )

            exec_dur = round(time.time() - exec_start, 3)
            action_result.duration_sec = exec_dur
            node.result = action_result

            # Record attempt history
            attempt_rec = {
                "attempt": node.retry_count + 1,
                "timestamp": time.time(),
                "success": action_result.success,
                "error": action_result.error_message,
            }
            node.attempt_history.append(attempt_rec)

            self.working_memory_manager.record_action(
                graph.task_id,
                {
                    "node_id": node.node_id,
                    "action": action.model_dump() if hasattr(action, "model_dump") else str(action),
                    "result": action_result.model_dump() if hasattr(action_result, "model_dump") else str(action_result),
                },
            )

            # 4. WorldState POST-execution observation
            post_snapshot = self.world_state_engine.refresh()
            post_obs_dict = post_snapshot.to_dict() if hasattr(post_snapshot, "to_dict") else str(post_snapshot)
            self.working_memory_manager.record_observation(graph.task_id, {"node_id": node.node_id, "post_execution": post_obs_dict})

            # 5. Outcome Verification
            if action_result.success:
                node.transition_to(NodeState.VERIFYING, "Action execution succeeded, initiating verification")
                expected_state = node.expected_state or action.action_type or "completed"

                obs_data = {
                    "world_state": post_snapshot.to_dict() if hasattr(post_snapshot, "to_dict") else post_snapshot,
                    "output": action_result.output,
                    "details": str(action_result.output or action_result.error_message or ""),
                    "verified": action_result.success,
                    "confidence": 0.95 if action_result.success else 0.0,
                }

                ver_res: VerificationResult = self.verification_engine.verify_action_outcome(
                    action_id=action.action_id,
                    expected_state=expected_state,
                    observed_state=obs_data,
                )
                node.verification = ver_res

                self.working_memory_manager.record_verification(
                    graph.task_id,
                    {
                        "node_id": node.node_id,
                        "verification": ver_res.model_dump() if hasattr(ver_res, "model_dump") else str(ver_res),
                    },
                )

                if ver_res.verified:
                    node.transition_to(NodeState.SUCCEEDED, "Action and outcome verification succeeded")
                    self.working_memory_manager.complete_node(graph.task_id, node.node_id)
                    return True
                else:
                    node.last_error = f"Verification failed: {ver_res.details}"
                    node.failure_reason = ver_res.details
                    node.failure_category = "VERIFICATION_FAILURE"
            else:
                node.last_error = action_result.error_message
                node.failure_reason = action_result.error_message
                node.failure_category = "ACTION_FAILURE"

            # 6. Retry Logic Assessment
            node.retry_count += 1

            if node.retry_count < node.max_retries and wm_task.retries_used < wm_task.max_retries:
                logger.info(
                    "Retrying failed node action",
                    node_id=node.node_id,
                    retry_count=node.retry_count,
                    max_retries=node.max_retries,
                )
                self.working_memory_manager.record_recovery_attempt(
                    graph.task_id,
                    {"node_id": node.node_id, "retry_attempt": node.retry_count, "error": node.last_error},
                )
                node.transition_to(NodeState.RUNNING, "Re-entering RUNNING state for retry attempt")
                continue
            else:
                logger.warning("Node failed and exhausted retries", node_id=node.node_id, retries=node.retry_count)
                node.transition_to(NodeState.FAILED, f"Failed after {node.retry_count} attempts: {node.last_error}")
                self.working_memory_manager.fail_node(graph.task_id, node.node_id, node.last_error or "Retries exhausted")
                return False

    def _cancel_remaining_nodes(self, graph: TaskGraph, reason: str) -> None:
        """Transitions remaining pending/ready nodes to CANCELLED."""
        for node in graph.nodes.values():
            if node.state in {NodeState.PENDING, NodeState.READY}:
                try:
                    node.transition_to(NodeState.CANCELLED, reason)
                except InvalidStateTransitionError:
                    pass

    def _build_result(
        self,
        graph: TaskGraph,
        status: TaskGraphStatus,
        executed: int,
        succeeded: int,
        failed: int,
        blocked: int,
        skipped: int,
        start_time: float,
        error_msg: str,
    ) -> TaskGraphResult:
        end_time = time.time()
        return TaskGraphResult(
            graph_id=graph.graph_id,
            task_id=graph.task_id,
            status=status,
            executed_nodes_count=executed,
            succeeded_nodes_count=succeeded,
            failed_nodes_count=failed,
            blocked_nodes_count=blocked,
            skipped_nodes_count=skipped,
            error_message=error_msg,
            start_time=start_time,
            end_time=end_time,
            duration_sec=round(end_time - start_time, 3),
        )
