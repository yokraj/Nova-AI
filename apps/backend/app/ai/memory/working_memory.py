"""Volatile Task-Scoped Working Memory Blackboard for Nova-AI.

Serves as an execution context tracking active tasks, current nodes, action history,
observations, verification results, recovery metrics, budgets, and plan versions.
Operates strictly as volatile, short-lived task memory independent of long-term vector/KG stores.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import copy
import threading
import time
import structlog

logger = structlog.get_logger("working_memory")


class TaskStatus(str, Enum):
    """Task status lifecycle."""

    CREATED = "CREATED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    PAUSED = "PAUSED"


@dataclass
class WorkingMemoryTask:
    """Volatile task execution context."""

    task_id: str
    user_goal: str
    task_status: TaskStatus = TaskStatus.CREATED
    current_node: Optional[str] = None
    completed_nodes: List[str] = field(default_factory=list)
    pending_nodes: List[str] = field(default_factory=list)
    failed_nodes: List[str] = field(default_factory=list)

    # Planning
    current_plan: List[Dict[str, Any]] = field(default_factory=list)
    current_plan_version: int = 1
    assumptions: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)

    # Execution
    current_action: Optional[Dict[str, Any]] = None
    action_history: List[Dict[str, Any]] = field(default_factory=list)
    action_outputs: List[Dict[str, Any]] = field(default_factory=list)
    observations: List[Dict[str, Any]] = field(default_factory=list)
    verification_results: List[Dict[str, Any]] = field(default_factory=list)

    # Recovery
    failure_count: int = 0
    retry_count: int = 0
    last_error: Optional[str] = None
    recovery_attempts: List[Dict[str, Any]] = field(default_factory=list)
    replanning_required: bool = False

    # Context
    retrieved_memory_ids: List[str] = field(default_factory=list)
    relevant_tool_ids: List[str] = field(default_factory=list)
    relevant_knowledge_graph_refs: List[str] = field(default_factory=list)

    # Result
    partial_results: List[Dict[str, Any]] = field(default_factory=list)
    final_result: Optional[Dict[str, Any]] = None
    goal_verification_status: str = "UNVERIFIED"

    # Phase 10F Plan Critic & Goal Verification
    goal_requirements: List[Dict[str, Any]] = field(default_factory=list)
    critic_result: Optional[Dict[str, Any]] = None
    goal_verification_details: Optional[Dict[str, Any]] = None
    failed_requirements: List[str] = field(default_factory=list)
    unresolved_uncertainty: List[str] = field(default_factory=list)
    verification_attempt_count: int = 0
    replan_context: Optional[Dict[str, Any]] = None

    # Phase 10G Failure Diagnosis & Replanning
    failure_history: List[Dict[str, Any]] = field(default_factory=list)
    known_bad_actions: List[Dict[str, Any]] = field(default_factory=list)
    plan_history: List[Dict[str, Any]] = field(default_factory=list)
    rejected_recovery_attempts: List[Dict[str, Any]] = field(default_factory=list)
    successful_recoveries: List[Dict[str, Any]] = field(default_factory=list)
    replan_count: int = 0
    max_replans: int = 3
    execution_control_state: str = "CONTINUE"

    # Budget
    steps_used: int = 0
    max_steps: int = 50
    retries_used: int = 0
    max_retries: int = 10
    start_time: float = field(default_factory=time.time)
    time_budget_sec: float = 3600.0

    # Phase 10H Long-Horizon Budget & Persistence
    model_calls_used: int = 0
    max_model_calls: int = 50
    estimated_tokens_used: int = 0
    max_estimated_tokens: int = 100000
    deadline_timestamp: Optional[float] = None

    @property
    def is_budget_exceeded(self) -> bool:
        """Returns True if step count, replans, model calls, or time exceeds assigned task budget."""
        if self.steps_used >= self.max_steps:
            return True
        if self.replan_count >= self.max_replans:
            return True
        if self.model_calls_used >= self.max_model_calls:
            return True
        if (time.time() - self.start_time) > self.time_budget_sec:
            return True
        if self.deadline_timestamp and time.time() > self.deadline_timestamp:
            return True
        return False

    def snapshot(self) -> Dict[str, Any]:
        """Returns deep copy dictionary snapshot to prevent external mutation."""
        return {
            "task_id": self.task_id,
            "user_goal": self.user_goal,
            "task_status": self.task_status.value if hasattr(self.task_status, "value") else str(self.task_status),
            "current_node": self.current_node,
            "completed_nodes": list(self.completed_nodes),
            "pending_nodes": list(self.pending_nodes),
            "failed_nodes": list(self.failed_nodes),
            "current_plan": copy.deepcopy(self.current_plan),
            "current_plan_version": self.current_plan_version,
            "assumptions": list(self.assumptions),
            "constraints": list(self.constraints),
            "current_action": copy.deepcopy(self.current_action),
            "action_history": copy.deepcopy(self.action_history),
            "action_outputs": copy.deepcopy(self.action_outputs),
            "observations": copy.deepcopy(self.observations),
            "verification_results": copy.deepcopy(self.verification_results),
            "failure_count": self.failure_count,
            "retry_count": self.retry_count,
            "last_error": self.last_error,
            "recovery_attempts": copy.deepcopy(self.recovery_attempts),
            "replanning_required": self.replanning_required,
            "retrieved_memory_ids": list(self.retrieved_memory_ids),
            "relevant_tool_ids": list(self.relevant_tool_ids),
            "relevant_knowledge_graph_refs": list(self.relevant_knowledge_graph_refs),
            "partial_results": copy.deepcopy(self.partial_results),
            "final_result": copy.deepcopy(self.final_result),
            "goal_verification_status": self.goal_verification_status,
            "goal_requirements": copy.deepcopy(self.goal_requirements),
            "critic_result": copy.deepcopy(self.critic_result),
            "goal_verification_details": copy.deepcopy(self.goal_verification_details),
            "failed_requirements": list(self.failed_requirements),
            "unresolved_uncertainty": list(self.unresolved_uncertainty),
            "verification_attempt_count": self.verification_attempt_count,
            "replan_context": copy.deepcopy(self.replan_context),
            "failure_history": copy.deepcopy(self.failure_history),
            "known_bad_actions": copy.deepcopy(self.known_bad_actions),
            "plan_history": copy.deepcopy(self.plan_history),
            "rejected_recovery_attempts": copy.deepcopy(self.rejected_recovery_attempts),
            "successful_recoveries": copy.deepcopy(self.successful_recoveries),
            "replan_count": self.replan_count,
            "max_replans": self.max_replans,
            "execution_control_state": self.execution_control_state,
            "steps_used": self.steps_used,
            "max_steps": self.max_steps,
            "retries_used": self.retries_used,
            "max_retries": self.max_retries,
            "start_time": self.start_time,
            "time_budget_sec": self.time_budget_sec,
            "model_calls_used": self.model_calls_used,
            "max_model_calls": self.max_model_calls,
            "estimated_tokens_used": self.estimated_tokens_used,
            "max_estimated_tokens": self.max_estimated_tokens,
            "deadline_timestamp": self.deadline_timestamp,
            "is_budget_exceeded": self.is_budget_exceeded,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkingMemoryTask":
        """Reconstructs WorkingMemoryTask instance from snapshot dictionary."""
        d = copy.deepcopy(data)
        d.pop("is_budget_exceeded", None)
        status_str = d.get("task_status", TaskStatus.CREATED.value)
        try:
            status_enum = TaskStatus(status_str)
        except ValueError:
            status_enum = TaskStatus.CREATED
        d["task_status"] = status_enum

        valid_fields = cls.__dataclass_fields__.keys()
        filtered = {k: v for k, v in d.items() if k in valid_fields}
        return cls(**filtered)


class WorkingMemoryManager:
    """Thread-safe manager controlling volatile WorkingMemory task blackboards."""

    _instance: Optional["WorkingMemoryManager"] = None
    _lock = threading.Lock()

    def __init__(self):
        self._memory_lock = threading.Lock()
        self._tasks: Dict[str, WorkingMemoryTask] = {}

    @classmethod
    def get_instance(cls) -> "WorkingMemoryManager":
        """Singleton accessor."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def create_task(
        self,
        task_id: str,
        user_goal: str,
        max_steps: int = 50,
        max_retries: int = 3,
        time_budget_sec: float = 3600.0,
    ) -> WorkingMemoryTask:
        """Initializes a new task blackboard."""
        with self._memory_lock:
            task = WorkingMemoryTask(
                task_id=task_id,
                user_goal=user_goal,
                max_steps=max_steps,
                max_retries=max_retries,
                time_budget_sec=time_budget_sec,
            )
            self._tasks[task_id] = task
            logger.info("Created working memory task", task_id=task_id, goal=user_goal)
            return task

    def get_task(self, task_id: str) -> Optional[WorkingMemoryTask]:
        """Retrieves raw task object for internal engine operations."""
        with self._memory_lock:
            return self._tasks.get(task_id)

    def get_snapshot(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves immutable dictionary snapshot for safe external reading."""
        with self._memory_lock:
            task = self._tasks.get(task_id)
            return task.snapshot() if task else None

    def set_current_node(self, task_id: str, node_id: str):
        """Sets active execution node."""
        with self._memory_lock:
            task = self._tasks.get(task_id)
            if task:
                task.current_node = node_id
                if task.task_status == TaskStatus.CREATED:
                    task.task_status = TaskStatus.RUNNING

    def complete_node(self, task_id: str, node_id: str):
        """Marks a node as completed and increments step count."""
        with self._memory_lock:
            task = self._tasks.get(task_id)
            if task:
                if node_id not in task.completed_nodes:
                    task.completed_nodes.append(node_id)
                if node_id in task.pending_nodes:
                    task.pending_nodes.remove(node_id)
                task.steps_used += 1

    def fail_node(self, task_id: str, node_id: str, error_reason: str):
        """Marks a node as failed and records error."""
        with self._memory_lock:
            task = self._tasks.get(task_id)
            if task:
                if node_id not in task.failed_nodes:
                    task.failed_nodes.append(node_id)
                task.failure_count += 1
                task.last_error = error_reason
                task.replanning_required = True

    def record_action(self, task_id: str, action_data: Dict[str, Any]):
        """Records executed action to history."""
        with self._memory_lock:
            task = self._tasks.get(task_id)
            if task:
                entry = dict(action_data)
                entry["recorded_at"] = time.time()
                task.current_action = entry
                task.action_history.append(entry)

    def record_observation(self, task_id: str, observation_data: Dict[str, Any]):
        """Records environment observation."""
        with self._memory_lock:
            task = self._tasks.get(task_id)
            if task:
                entry = dict(observation_data)
                entry["recorded_at"] = time.time()
                task.observations.append(entry)

    def record_verification(self, task_id: str, verification_data: Dict[str, Any]):
        """Records action/goal verification outcome."""
        with self._memory_lock:
            task = self._tasks.get(task_id)
            if task:
                entry = dict(verification_data)
                entry["recorded_at"] = time.time()
                task.verification_results.append(entry)

    def record_critic_result(self, task_id: str, critic_data: Dict[str, Any]):
        """Records Phase 10F PlanCritic result in task working memory."""
        with self._memory_lock:
            task = self._tasks.get(task_id)
            if task:
                task.critic_result = copy.deepcopy(critic_data)
                if "missing_requirements" in critic_data:
                    task.failed_requirements = list(critic_data["missing_requirements"])

    def record_goal_verification_details(self, task_id: str, verification_details: Dict[str, Any]):
        """Records Phase 10F GoalVerifier outcome and replan context in task working memory."""
        with self._memory_lock:
            task = self._tasks.get(task_id)
            if task:
                task.goal_verification_details = copy.deepcopy(verification_details)
                task.goal_verification_status = verification_details.get("status", "UNVERIFIED")
                task.failed_requirements = list(verification_details.get("failed_requirement_ids", []))
                task.unresolved_uncertainty = list(verification_details.get("unverified_requirement_ids", []))
                task.replan_context = copy.deepcopy(verification_details.get("replan_context"))
                task.verification_attempt_count += 1

    def record_recovery_attempt(self, task_id: str, recovery_data: Dict[str, Any]):
        """Records recovery attempt and increments retry count."""
        with self._memory_lock:
            task = self._tasks.get(task_id)
            if task:
                entry = dict(recovery_data)
                entry["recorded_at"] = time.time()
                task.recovery_attempts.append(entry)
                task.retry_count += 1
                task.retries_used += 1

    def set_plan(self, task_id: str, plan_steps: List[Dict[str, Any]]):
        """Assigns structured execution plan."""
        with self._memory_lock:
            task = self._tasks.get(task_id)
            if task:
                task.current_plan = copy.deepcopy(plan_steps)
                task.pending_nodes = [step.get("id", f"step_{i}") for i, step in enumerate(plan_steps)]

    def increment_plan_version(self, task_id: str):
        """Increments plan version upon replanning."""
        with self._memory_lock:
            task = self._tasks.get(task_id)
            if task:
                task.current_plan_version += 1
                task.replan_count += 1
                task.replanning_required = False

    def record_failure_diagnosis(self, task_id: str, diagnosis_data: Dict[str, Any]):
        """Records Phase 10G FailureDiagnosis in task working memory."""
        with self._memory_lock:
            task = self._tasks.get(task_id)
            if task:
                entry = copy.deepcopy(diagnosis_data)
                entry["recorded_at"] = time.time()
                task.failure_history.append(entry)
                task.last_error = entry.get("root_cause", task.last_error)

    def record_known_bad_action(self, task_id: str, action_spec: Dict[str, Any]):
        """Blacklists a known-bad action spec to prevent repeating failed actions."""
        with self._memory_lock:
            task = self._tasks.get(task_id)
            if task:
                entry = copy.deepcopy(action_spec)
                if entry not in task.known_bad_actions:
                    task.known_bad_actions.append(entry)

    def record_plan_version(self, task_id: str, plan_steps: List[Dict[str, Any]], reason: str):
        """Records plan version snapshot and replan reason in plan history."""
        with self._memory_lock:
            task = self._tasks.get(task_id)
            if task:
                entry = {
                    "version": task.current_plan_version,
                    "plan": copy.deepcopy(plan_steps),
                    "reason": reason,
                    "recorded_at": time.time(),
                }
                task.plan_history.append(entry)
                task.current_plan = copy.deepcopy(plan_steps)

    def record_rejected_recovery(self, task_id: str, recovery_data: Dict[str, Any]):
        """Records a rejected recovery attempt."""
        with self._memory_lock:
            task = self._tasks.get(task_id)
            if task:
                entry = copy.deepcopy(recovery_data)
                entry["recorded_at"] = time.time()
                task.rejected_recovery_attempts.append(entry)

    def record_successful_recovery(self, task_id: str, recovery_data: Dict[str, Any]):
        """Records a successful recovery event."""
        with self._memory_lock:
            task = self._tasks.get(task_id)
            if task:
                entry = copy.deepcopy(recovery_data)
                entry["recorded_at"] = time.time()
                task.successful_recoveries.append(entry)

    def set_execution_control_state(self, task_id: str, state: str):
        """Sets active ExecutionControlState for the task."""
        with self._memory_lock:
            task = self._tasks.get(task_id)
            if task:
                task.execution_control_state = state

    def set_result(self, task_id: str, final_result: Dict[str, Any], verification_status: str = "VERIFIED"):
        """Finalizes task outcome and status."""
        with self._memory_lock:
            task = self._tasks.get(task_id)
            if task:
                task.final_result = copy.deepcopy(final_result)
                task.goal_verification_status = verification_status
                task.task_status = TaskStatus.COMPLETED if verification_status == "VERIFIED" else TaskStatus.FAILED

    def clear_task(self, task_id: str):
        """Removes task context upon completion."""
        with self._memory_lock:
            if task_id in self._tasks:
                del self._tasks[task_id]
                logger.info("Cleared working memory task", task_id=task_id)
