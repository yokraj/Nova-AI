"""Durable Long-Horizon Task Manager for Nova-AI.

Orchestrates multi-step task execution, checkpoints, safe pause/resume, durable cancellation,
process restart recovery, budget enforcement, and structured progress reporting above the cognitive kernel.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import asyncio
import threading
import time
import structlog

from app.ai.desktop_automation.application_adapter import ApplicationAdapterRegistry
from app.ai.desktop_automation.models import AutomationAction
from app.ai.desktop_automation.world_state import WorldStateEngine
from app.ai.kernel.capability_discovery import CapabilityDiscoveryEngine
from app.ai.kernel.durable_checkpoint_store import DurableCheckpointStore, LongHorizonTaskCheckpoint
from app.ai.kernel.dynamic_replanner import DynamicReplanner
from app.ai.kernel.failure_diagnoser import ExecutionControlState, FailureDiagnoser
from app.ai.kernel.goal_verifier import GoalRequirement, GoalVerifier, VerificationStatus
from app.ai.kernel.plan_critic import CriticStatus, PlanCritic
from app.ai.kernel.task_graph import NodeState, TaskGraph, TaskGraphExecutor, TaskNode
from app.ai.memory.working_memory import TaskStatus, WorkingMemoryManager, WorkingMemoryTask

logger = structlog.get_logger("long_horizon_manager")


class DurableTaskState(str, Enum):
    """Explicit durable states for long-horizon tasks."""

    CREATED = "CREATED"
    QUEUED = "QUEUED"
    PLANNING = "PLANNING"
    CRITICIZING = "CRITICIZING"
    READY = "READY"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    WAITING = "WAITING"
    VERIFYING = "VERIFYING"
    RECOVERING = "RECOVERING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    BLOCKED = "BLOCKED"
    REQUIRES_HUMAN = "REQUIRES_HUMAN"


@dataclass
class TaskProgressReport:
    """Structured progress report reflecting empirical task graph state."""

    task_id: str
    user_goal: str
    durable_state: DurableTaskState
    plan_version: int
    total_nodes: int
    completed_nodes: int
    active_nodes: int
    blocked_nodes: int
    failed_nodes: int
    waiting_nodes: int
    current_phase: str
    percentage_complete: float
    goal_requirement_status: str
    latest_verification: Optional[Dict[str, Any]] = None
    latest_failure_recovery: Optional[Dict[str, Any]] = None
    waiting_reason: Optional[str] = None
    pause_reason: Optional[str] = None
    cancellation_reason: Optional[str] = None


@dataclass
class TaskExecutionSummary:
    """Outcome summary for a long-horizon task execution step or run."""

    task_id: str
    user_goal: str
    durable_state: DurableTaskState
    plan_version: int = 1
    executed_nodes_count: int = 0
    goal_satisfied: bool = False
    verification_result: Optional[Dict[str, Any]] = None
    replan_result: Optional[Dict[str, Any]] = None
    working_memory_snapshot: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class LongHorizonTaskManager:
    """Durable Long-Horizon Task Manager orchestrating cognitive execution lifecycle."""

    _instance: Optional["LongHorizonTaskManager"] = None
    _lock = threading.Lock()

    def __init__(
        self,
        checkpoint_store: Optional[DurableCheckpointStore] = None,
        working_memory: Optional[WorkingMemoryManager] = None,
        executor: Optional[TaskGraphExecutor] = None,
        verifier: Optional[GoalVerifier] = None,
        diagnoser: Optional[FailureDiagnoser] = None,
        replanner: Optional[DynamicReplanner] = None,
        critic: Optional[PlanCritic] = None,
        world_state: Optional[WorldStateEngine] = None,
    ):
        self.checkpoint_store = checkpoint_store or DurableCheckpointStore.get_instance()
        self.working_memory = working_memory or WorkingMemoryManager.get_instance()
        self.executor = executor or TaskGraphExecutor(adapter_registry=ApplicationAdapterRegistry.get_instance())
        self.verifier = verifier or GoalVerifier.get_instance()
        self.diagnoser = diagnoser or FailureDiagnoser.get_instance()
        self.replanner = replanner or DynamicReplanner.get_instance()
        self.critic = critic or PlanCritic.get_instance()
        self.world_state = world_state or WorldStateEngine.get_instance()

        self._task_locks: Dict[str, threading.Lock] = {}
        self._pause_requests: Dict[str, bool] = {}
        self._cancel_requests: Dict[str, bool] = {}

    @classmethod
    def get_instance(cls, checkpoint_store: Optional[DurableCheckpointStore] = None) -> "LongHorizonTaskManager":
        """Singleton accessor."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(checkpoint_store=checkpoint_store)
        return cls._instance

    def _get_lock(self, task_id: str) -> threading.Lock:
        with self._lock:
            if task_id not in self._task_locks:
                self._task_locks[task_id] = threading.Lock()
            return self._task_locks[task_id]

    def create_task(
        self,
        user_goal: str,
        budgets: Optional[Dict[str, Any]] = None,
        task_id: Optional[str] = None,
        initial_requirements: Optional[List[GoalRequirement]] = None,
    ) -> str:
        """Creates a new long-horizon task, initializes working memory and durable checkpoint."""
        budgets = budgets or {}
        wm_task = self.working_memory.create_task(
            task_id=task_id,
            user_goal=user_goal,
            max_steps=budgets.get("max_actions", 50),
            max_retries=budgets.get("max_retries", 10),
            time_budget_sec=budgets.get("max_execution_time_sec", 3600.0),
        )
        task_id = wm_task.task_id

        if "max_replans" in budgets:
            wm_task.max_replans = budgets["max_replans"]
        if "max_model_calls" in budgets:
            wm_task.max_model_calls = budgets["max_model_calls"]
        if "max_estimated_tokens" in budgets:
            wm_task.max_estimated_tokens = budgets["max_estimated_tokens"]
        if "deadline_timestamp" in budgets:
            wm_task.deadline_timestamp = budgets["deadline_timestamp"]

        if initial_requirements:
            wm_task.goal_requirements = [r.to_dict() for r in initial_requirements]

        checkpoint = LongHorizonTaskCheckpoint(
            task_id=task_id,
            user_goal=user_goal,
            durable_state=DurableTaskState.CREATED.value,
            working_memory_snapshot=wm_task.snapshot(),
            max_execution_time_sec=wm_task.time_budget_sec,
            max_actions=wm_task.max_steps,
            max_retries=wm_task.max_retries,
            max_replans=wm_task.max_replans,
            max_model_calls=wm_task.max_model_calls,
            max_estimated_tokens=wm_task.max_estimated_tokens,
            deadline_timestamp=wm_task.deadline_timestamp,
        )

        self.checkpoint_store.save_checkpoint(checkpoint)
        self.checkpoint_store.append_history_event(task_id, "TASK_CREATED", {"user_goal": user_goal, "budgets": budgets})

        self._pause_requests[task_id] = False
        self._cancel_requests[task_id] = False

        logger.info("Created durable long-horizon task", task_id=task_id, goal=user_goal)
        return task_id

    def transition_task_state(self, task_id: str, new_state: DurableTaskState, reason: str = "", extra_details: Optional[Dict[str, Any]] = None) -> None:
        """Explicitly transitions durable task state and updates persistent checkpoint."""
        lock = self._get_lock(task_id)
        with lock:
            checkpoint = self.checkpoint_store.load_checkpoint(task_id)
            if not checkpoint:
                raise ValueError(f"Task '{task_id}' does not exist in checkpoint store.")

            old_state = checkpoint.durable_state
            checkpoint.durable_state = new_state.value
            checkpoint.updated_at = time.time()

            if new_state == DurableTaskState.PAUSED:
                checkpoint.paused_at = time.time()
                checkpoint.pause_reason = reason
            elif new_state == DurableTaskState.CANCELLED:
                checkpoint.cancelled_at = time.time()
                checkpoint.cancellation_reason = reason
            elif new_state == DurableTaskState.WAITING:
                checkpoint.waiting_reason = reason

            wm_task = self.working_memory.get_task(task_id)
            if wm_task:
                wm_task.execution_control_state = new_state.value
                if new_state == DurableTaskState.PAUSED:
                    wm_task.task_status = TaskStatus.PAUSED
                elif new_state == DurableTaskState.CANCELLED:
                    wm_task.task_status = TaskStatus.CANCELLED
                elif new_state == DurableTaskState.COMPLETED:
                    wm_task.task_status = TaskStatus.COMPLETED
                elif new_state == DurableTaskState.FAILED:
                    wm_task.task_status = TaskStatus.FAILED
                checkpoint.working_memory_snapshot = wm_task.snapshot()

            self.checkpoint_store.save_checkpoint(checkpoint)
            evt_details = {"old_state": old_state, "new_state": new_state.value, "reason": reason}
            if extra_details:
                evt_details.update(extra_details)
            self.checkpoint_store.append_history_event(task_id, "STATE_TRANSITION", evt_details)

            logger.info("Transitioned durable task state", task_id=task_id, old=old_state, new=new_state.value, reason=reason)

    def pause_task(self, task_id: str, reason: str = "User requested pause") -> bool:
        """Flags pause request and safely transitions state to PAUSED."""
        checkpoint = self.checkpoint_store.load_checkpoint(task_id)
        if not checkpoint:
            return False

        if checkpoint.durable_state in (DurableTaskState.COMPLETED.value, DurableTaskState.FAILED.value, DurableTaskState.CANCELLED.value):
            logger.warning("Cannot pause terminal task", task_id=task_id, state=checkpoint.durable_state)
            return False

        self._pause_requests[task_id] = True
        self.transition_task_state(task_id, DurableTaskState.PAUSED, reason=reason)
        return True

    def cancel_task(self, task_id: str, reason: str = "User requested cancellation") -> bool:
        """Flags cancellation and permanently sets state to CANCELLED."""
        checkpoint = self.checkpoint_store.load_checkpoint(task_id)
        if not checkpoint:
            return False

        self._cancel_requests[task_id] = True
        self.transition_task_state(task_id, DurableTaskState.CANCELLED, reason=reason)
        return True

    def _check_budget_limits(self, checkpoint: LongHorizonTaskCheckpoint, wm_task: WorkingMemoryTask) -> Optional[DurableTaskState]:
        """Evaluates whether any configured task budget is exhausted."""
        now = time.time()
        elapsed = now - checkpoint.created_at
        checkpoint.elapsed_time_sec = elapsed

        if checkpoint.max_execution_time_sec and elapsed > checkpoint.max_execution_time_sec:
            logger.warning("Budget limit triggered: execution_time", elapsed=elapsed, max_sec=checkpoint.max_execution_time_sec)
            return DurableTaskState.BLOCKED
        if checkpoint.deadline_timestamp and now > checkpoint.deadline_timestamp:
            logger.warning("Budget limit triggered: deadline_timestamp", now=now, deadline=checkpoint.deadline_timestamp)
            return DurableTaskState.BLOCKED
        if checkpoint.max_actions and checkpoint.actions_used >= checkpoint.max_actions:
            logger.warning("Budget limit triggered: actions_used", actions_used=checkpoint.actions_used, max_actions=checkpoint.max_actions)
            return DurableTaskState.BLOCKED
        if checkpoint.max_retries and checkpoint.retries_used >= checkpoint.max_retries:
            logger.warning("Budget limit triggered: retries_used", retries_used=checkpoint.retries_used, max_retries=checkpoint.max_retries)
            return DurableTaskState.BLOCKED
        if checkpoint.max_replans and checkpoint.replans_used >= checkpoint.max_replans:
            logger.warning("Budget limit triggered: replans_used", replans_used=checkpoint.replans_used, max_replans=checkpoint.max_replans)
            return DurableTaskState.REQUIRES_HUMAN
        if checkpoint.max_model_calls and checkpoint.model_calls_used >= checkpoint.max_model_calls:
            logger.warning("Budget limit triggered: model_calls_used", model_calls_used=checkpoint.model_calls_used, max_calls=checkpoint.max_model_calls)
            return DurableTaskState.REQUIRES_HUMAN
        if checkpoint.max_estimated_tokens and checkpoint.tokens_used >= checkpoint.max_estimated_tokens:
            logger.warning("Budget limit triggered: tokens_used", tokens_used=checkpoint.tokens_used, max_tokens=checkpoint.max_estimated_tokens)
            return DurableTaskState.REQUIRES_HUMAN

        if wm_task.is_budget_exceeded:
            logger.warning("Budget limit triggered: wm_task.is_budget_exceeded", steps=wm_task.steps_used, replans=wm_task.replan_count, model_calls=wm_task.model_calls_used)
            return DurableTaskState.BLOCKED

        return None

    def _sync_checkpoint_from_graph(self, checkpoint: LongHorizonTaskCheckpoint, graph: TaskGraph, wm_task: WorkingMemoryTask) -> None:
        """Synchronizes checkpoint arrays and stats from current TaskGraph and WorkingMemory."""
        checkpoint.task_graph_dict = graph.to_dict()
        checkpoint.completed_nodes = [n.node_id for n in graph.nodes.values() if n.state == NodeState.SUCCEEDED]
        checkpoint.running_nodes = [n.node_id for n in graph.nodes.values() if n.state == NodeState.RUNNING]
        checkpoint.failed_nodes = [n.node_id for n in graph.nodes.values() if n.state == NodeState.FAILED]
        checkpoint.waiting_nodes = [n.node_id for n in graph.nodes.values() if n.state == NodeState.WAITING]
        checkpoint.blocked_nodes = [n.node_id for n in graph.nodes.values() if n.state == NodeState.BLOCKED]

        checkpoint.actions_used = len(checkpoint.completed_nodes) + len(checkpoint.failed_nodes)
        checkpoint.retries_used = sum(n.retry_count for n in graph.nodes.values())
        checkpoint.replans_used = wm_task.replan_count
        checkpoint.working_memory_snapshot = wm_task.snapshot()
        checkpoint.world_state_references = self.world_state.get_snapshot().to_dict()

    async def execute_task_lifecycle(
        self,
        task_id: str,
        graph: Optional[TaskGraph] = None,
        requirements: Optional[List[GoalRequirement]] = None,
        adapter_name: Optional[str] = None,
    ) -> TaskExecutionSummary:
        """Executes full long-horizon task lifecycle through kernel components."""
        lock = self._get_lock(task_id)
        with lock:
            checkpoint = self.checkpoint_store.load_checkpoint(task_id)
            if not checkpoint:
                return TaskExecutionSummary(task_id=task_id, user_goal="", durable_state=DurableTaskState.FAILED, error="Task checkpoint not found.")

            # Durable Cancellation Guard
            if checkpoint.durable_state == DurableTaskState.CANCELLED.value or self._cancel_requests.get(task_id):
                self.transition_task_state(task_id, DurableTaskState.CANCELLED, reason="Task cancelled prior to execution")
                return TaskExecutionSummary(
                    task_id=task_id,
                    user_goal=checkpoint.user_goal,
                    durable_state=DurableTaskState.CANCELLED,
                    error="Task is cancelled.",
                )

            # Pause Guard
            if checkpoint.durable_state == DurableTaskState.PAUSED.value or self._pause_requests.get(task_id):
                return TaskExecutionSummary(
                    task_id=task_id,
                    user_goal=checkpoint.user_goal,
                    durable_state=DurableTaskState.PAUSED,
                    error="Task is paused.",
                )

        wm_task = self.working_memory.get_task(task_id)
        if not wm_task:
            wm_task = WorkingMemoryTask.from_dict(checkpoint.working_memory_snapshot)
            self.working_memory._tasks[task_id] = wm_task

        # Restore or initialize TaskGraph
        if graph is None and checkpoint.task_graph_dict:
            graph = TaskGraph.from_dict(checkpoint.task_graph_dict)
        elif graph is None:
            # Fallback auto-discovery initial graph if none provided
            disc = CapabilityDiscoveryEngine.get_instance()
            matched = disc.discover_capabilities_sync(checkpoint.user_goal, top_k=3)
            graph = TaskGraph(task_id=task_id)
            for i, c in enumerate(matched):
                node = TaskNode(
                    node_id=f"node_{i+1}_{c.capability_id}",
                    title=c.name,
                    action=AutomationAction(
                        action_id=f"act_{i+1}",
                        action_type=c.action_type,
                        target_label=c.application,
                    ),
                )
                graph.add_node(node)

        # 1. PLANNING & CRITICIZING
        self.transition_task_state(task_id, DurableTaskState.PLANNING)
        self.transition_task_state(task_id, DurableTaskState.CRITICIZING)

        critic_res = self.critic.evaluate_plan(graph=graph, user_goal=checkpoint.user_goal)
        wm_task.critic_result = critic_res.to_dict()

        if critic_res.status == CriticStatus.REJECTED:
            self.transition_task_state(task_id, DurableTaskState.FAILED, reason=f"Plan rejected by PlanCritic: {critic_res.issues}")
            return TaskExecutionSummary(
                task_id=task_id,
                user_goal=checkpoint.user_goal,
                durable_state=DurableTaskState.FAILED,
                error=f"Plan rejected: {critic_res.issues}",
            )

        self.transition_task_state(task_id, DurableTaskState.READY)
        self.transition_task_state(task_id, DurableTaskState.RUNNING)

        # Check budget limits before loop
        exceeded_state = self._check_budget_limits(checkpoint, wm_task)
        if exceeded_state:
            self.transition_task_state(task_id, exceeded_state, reason="Initial budget limit exceeded")
            return TaskExecutionSummary(
                task_id=task_id,
                user_goal=checkpoint.user_goal,
                durable_state=exceeded_state,
                error="Task budget limit exceeded.",
            )

        # 2. EXECUTION LOOP WITH RECOVERY & CHECKPOINTING
        exec_res = await self.executor.execute(graph=graph, user_goal=checkpoint.user_goal)
        self._sync_checkpoint_from_graph(checkpoint, graph, wm_task)
        self.checkpoint_store.save_checkpoint(checkpoint)

        # Check for pause / cancel requests during execution
        if self._cancel_requests.get(task_id):
            self.transition_task_state(task_id, DurableTaskState.CANCELLED, reason="Cancelled during execution")
            return TaskExecutionSummary(task_id=task_id, user_goal=checkpoint.user_goal, durable_state=DurableTaskState.CANCELLED)

        if self._pause_requests.get(task_id):
            self.transition_task_state(task_id, DurableTaskState.PAUSED, reason="Paused during execution")
            return TaskExecutionSummary(task_id=task_id, user_goal=checkpoint.user_goal, durable_state=DurableTaskState.PAUSED)

        # 3. FAILURE DIAGNOSIS & DYNAMIC REPLANNING (IF FAILED)
        if exec_res.status.value in ("failed", "partial"):
            self.transition_task_state(task_id, DurableTaskState.RECOVERING)
            failed_node_id = checkpoint.failed_nodes[0] if checkpoint.failed_nodes else "unknown_node"
            failed_node = graph.nodes.get(failed_node_id)
            act_res = failed_node.result.model_dump() if (failed_node and failed_node.result) else {"error": "Execution failed"}

            diag = self.diagnoser.diagnose_failure(
                task_id=task_id,
                user_goal=checkpoint.user_goal,
                node_id=failed_node_id,
                action_result=act_res,
            )

            if diag.requires_human or diag.recoverability.value == "HUMAN_REQUIRED":
                self.transition_task_state(task_id, DurableTaskState.REQUIRES_HUMAN, reason=f"Diagnosis requires human: {diag.root_cause}")
                return TaskExecutionSummary(task_id=task_id, user_goal=checkpoint.user_goal, durable_state=DurableTaskState.REQUIRES_HUMAN, error=diag.root_cause)

            replan_res = self.replanner.replan(
                task_id=task_id,
                user_goal=checkpoint.user_goal,
                current_graph=graph,
                diagnosis=diag,
                working_memory_task=wm_task,
            )

            if replan_res.control_state in (ExecutionControlState.REPLAN, ExecutionControlState.RETRY) and replan_res.new_graph:
                checkpoint.replans_used += 1
                checkpoint.current_plan_version = replan_res.plan_version
                graph = replan_res.new_graph
                # Re-run recovery plan physically
                exec_res = await self.executor.execute(graph=graph, user_goal=checkpoint.user_goal)
                self._sync_checkpoint_from_graph(checkpoint, graph, wm_task)
                self.checkpoint_store.save_checkpoint(checkpoint)
            else:
                self.transition_task_state(task_id, DurableTaskState.FAILED, reason=f"Replanning failed: {replan_res.reason}")
                return TaskExecutionSummary(task_id=task_id, user_goal=checkpoint.user_goal, durable_state=DurableTaskState.FAILED, error=replan_res.reason)

        # 4. GOAL VERIFICATION
        self.transition_task_state(task_id, DurableTaskState.VERIFYING)
        reqs = requirements or [GoalRequirement(req_id="req_1", description=checkpoint.user_goal, target_state="SUCCESS")]
        g_res = self.verifier.verify_goal(
            task_id=task_id,
            user_goal=checkpoint.user_goal,
            requirements=reqs,
            execution_summary={"status": "SUCCESS" if exec_res.status.value == "success" else "FAILED"},
            adapter_name=adapter_name,
        )

        checkpoint.verification_status = g_res.status.value
        self.checkpoint_store.save_checkpoint(checkpoint)

        if g_res.status == VerificationStatus.SUCCESS or g_res.goal_satisfied:
            self.transition_task_state(task_id, DurableTaskState.COMPLETED, reason="Goal verified successfully")
            return TaskExecutionSummary(
                task_id=task_id,
                user_goal=checkpoint.user_goal,
                durable_state=DurableTaskState.COMPLETED,
                plan_version=checkpoint.current_plan_version,
                executed_nodes_count=exec_res.executed_nodes_count,
                goal_satisfied=True,
                verification_result=g_res.to_dict(),
                working_memory_snapshot=wm_task.snapshot(),
            )
        else:
            self.transition_task_state(task_id, DurableTaskState.FAILED, reason="Goal verification failed")
            return TaskExecutionSummary(
                task_id=task_id,
                user_goal=checkpoint.user_goal,
                durable_state=DurableTaskState.FAILED,
                plan_version=checkpoint.current_plan_version,
                executed_nodes_count=exec_res.executed_nodes_count,
                goal_satisfied=False,
                verification_result=g_res.to_dict(),
                working_memory_snapshot=wm_task.snapshot(),
                error="Goal verification failed",
            )

    def start_task(
        self,
        task_id: str,
        graph: Optional[TaskGraph] = None,
        requirements: Optional[List[GoalRequirement]] = None,
        adapter_name: Optional[str] = None,
    ) -> TaskExecutionSummary:
        """Starts task execution synchronously/async wrapper."""
        return asyncio.run(self.execute_task_lifecycle(task_id=task_id, graph=graph, requirements=requirements, adapter_name=adapter_name))

    def resume_task(
        self,
        task_id: str,
        requirements: Optional[List[GoalRequirement]] = None,
        adapter_name: Optional[str] = None,
    ) -> TaskExecutionSummary:
        """Resumes a paused or stopped task from its latest checkpoint."""
        checkpoint = self.checkpoint_store.load_checkpoint(task_id)
        if not checkpoint:
            return TaskExecutionSummary(task_id=task_id, user_goal="", durable_state=DurableTaskState.FAILED, error="Checkpoint not found")

        if checkpoint.durable_state == DurableTaskState.CANCELLED.value:
            logger.warning("Attempted to resume cancelled task", task_id=task_id)
            return TaskExecutionSummary(task_id=task_id, user_goal=checkpoint.user_goal, durable_state=DurableTaskState.CANCELLED, error="Cannot resume cancelled task.")

        self._pause_requests[task_id] = False
        self.transition_task_state(task_id, DurableTaskState.READY, reason="Resumed from checkpoint")
        return asyncio.run(self.execute_task_lifecycle(task_id=task_id, requirements=requirements, adapter_name=adapter_name))

    def recover_on_restart(
        self,
        task_id: str,
        requirements: Optional[List[GoalRequirement]] = None,
        adapter_name: Optional[str] = None,
    ) -> TaskExecutionSummary:
        """Recovers task after process restart, refreshes WorldState, detects stale state, and resumes."""
        checkpoint = self.checkpoint_store.load_checkpoint(task_id)
        if not checkpoint:
            return TaskExecutionSummary(task_id=task_id, user_goal="", durable_state=DurableTaskState.FAILED, error="Checkpoint not found for restart recovery")

        # Durable cancellation enforcement
        if checkpoint.durable_state == DurableTaskState.CANCELLED.value:
            logger.info("Task remains CANCELLED after process restart", task_id=task_id)
            return TaskExecutionSummary(task_id=task_id, user_goal=checkpoint.user_goal, durable_state=DurableTaskState.CANCELLED, error="Task was cancelled")

        if checkpoint.durable_state in (DurableTaskState.COMPLETED.value, DurableTaskState.FAILED.value):
            return TaskExecutionSummary(task_id=task_id, user_goal=checkpoint.user_goal, durable_state=DurableTaskState(checkpoint.durable_state))

        # Stale state detection: Compare current WorldState with checkpoint snapshot
        current_ws = self.world_state.get_snapshot()
        stored_ws_ref = checkpoint.world_state_references

        stale_detected = False
        if stored_ws_ref:
            stored_app = stored_ws_ref.get("application", {}).get("active_app_name", {}).get("value")
            current_app = current_ws.application.active_app_name.value
            if stored_app and stored_app != "UNKNOWN" and current_app != "UNKNOWN" and stored_app != current_app:
                stale_detected = True
                logger.warning("Stale environment state detected on restart", task_id=task_id, stored=stored_app, current=current_app)

        self.checkpoint_store.append_history_event(task_id, "PROCESS_RESTART_RECOVERY", {"stale_detected": stale_detected, "durable_state": checkpoint.durable_state})

        self.transition_task_state(task_id, DurableTaskState.RECOVERING, reason="Process restart recovery initiated")
        return asyncio.run(self.execute_task_lifecycle(task_id=task_id, requirements=requirements, adapter_name=adapter_name))

    def get_task_progress(self, task_id: str) -> TaskProgressReport:
        """Returns structured progress report reflecting current task graph state."""
        checkpoint = self.checkpoint_store.load_checkpoint(task_id)
        if not checkpoint:
            raise ValueError(f"Task '{task_id}' not found.")

        graph_dict = checkpoint.task_graph_dict
        total = len(graph_dict.get("nodes", {})) if graph_dict else 0
        completed = len(checkpoint.completed_nodes)
        running = len(checkpoint.running_nodes)
        failed = len(checkpoint.failed_nodes)
        waiting = len(checkpoint.waiting_nodes)
        blocked = len(checkpoint.blocked_nodes)

        pct = (completed / total * 100.0) if total > 0 else (100.0 if checkpoint.durable_state == DurableTaskState.COMPLETED.value else 0.0)

        wm_task = self.working_memory.get_task(task_id)
        latest_ver = wm_task.goal_verification_details if wm_task else None
        latest_recovery = wm_task.successful_recoveries[-1] if (wm_task and wm_task.successful_recoveries) else None

        return TaskProgressReport(
            task_id=task_id,
            user_goal=checkpoint.user_goal,
            durable_state=DurableTaskState(checkpoint.durable_state),
            plan_version=checkpoint.current_plan_version,
            total_nodes=total,
            completed_nodes=completed,
            active_nodes=running,
            blocked_nodes=blocked,
            failed_nodes=failed,
            waiting_nodes=waiting,
            current_phase=checkpoint.durable_state,
            percentage_complete=round(pct, 2),
            goal_requirement_status=checkpoint.verification_status,
            latest_verification=latest_ver,
            latest_failure_recovery=latest_recovery,
            waiting_reason=checkpoint.waiting_reason,
            pause_reason=checkpoint.pause_reason,
            cancellation_reason=checkpoint.cancellation_reason,
        )

    def get_task_history(self, task_id: str) -> List[Dict[str, Any]]:
        """Returns complete immutable event history log for a task."""
        return self.checkpoint_store.get_task_history(task_id)
