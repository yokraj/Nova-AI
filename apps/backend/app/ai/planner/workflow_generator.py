"""Workflow Generator compiling final ExecutionPlan structures.
"""

from app.ai.planner.models import TaskTree, DependencyGraph, ExecutionPlan
from app.ai.planner.priority_engine import PriorityEngine
from app.ai.planner.agent_selector import AgentSelector
from app.ai.planner.execution_estimator import ExecutionEstimator
from app.ai.planner.scheduler import Scheduler
from app.ai.planner.optimizer import Optimizer
from app.ai.planner.validation import ValidationEngine
from app.ai.planner.recovery_planner import RecoveryPlanner

class WorkflowGenerator:
    """Assembles final batches, assignments, estimates, and recovery plans."""

    def __init__(
        self,
        priority: PriorityEngine,
        selector: AgentSelector,
        estimator: ExecutionEstimator,
        scheduler: Scheduler,
        optimizer: Optimizer,
        validator: ValidationEngine,
        recovery: RecoveryPlanner
    ) -> None:
        self.priority = priority
        self.selector = selector
        self.estimator = estimator
        self.scheduler = scheduler
        self.optimizer = optimizer
        self.validator = validator
        self.recovery = recovery

    def generate_workflow(self, task_tree: TaskTree, graph: DependencyGraph) -> ExecutionPlan:
        """Runs the compile pipeline: priorities, select, estimate, batch, optimize, validate, recovery."""
        # 1. Update task priority attributes and critical path lists
        self.priority.calculate_priorities(graph)

        # 2. Select agents and estimate resource limits
        for task in graph.nodes.values():
            task.assignment = self.selector.select_agent(task)
            self.estimator.estimate_task(task)

        # 3. Schedule task nodes into execution batches
        plan = self.scheduler.generate_plan(graph)

        # 4. Apply compression optimizations
        self.optimizer.optimize_plan(graph, plan)

        # 5. Assert DAG integrity rules
        self.validator.validate_graph(graph)

        # 6. Append recovery maps fallback instructions
        plan.recovery_plans = self.recovery.generate_recovery_plans(graph)

        return plan
