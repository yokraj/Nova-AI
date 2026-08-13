"""Planner Engine orchestrating goal analysis, recursive decompositions, and scheduling.
"""

import structlog
from typing import Optional, Any

from app.ai.planner.configuration import MultiAgentPlannerConfiguration
from app.ai.planner.models import (
    PlanningRequest,
    PlanningResponse,
    Goal,
    TaskTree,
    DependencyGraph,
    PlanningMetrics,
    ExecutionPlan,
    Task,
    TaskNode
)
from app.ai.planner.goal_analyzer import GoalAnalyzer
from app.ai.planner.decomposition_engine import DecompositionEngine
from app.ai.planner.dag_builder import DAGBuilder
from app.ai.planner.priority_engine import PriorityEngine
from app.ai.planner.capability_matcher import CapabilityMatcher
from app.ai.planner.agent_selector import AgentSelector
from app.ai.planner.execution_estimator import ExecutionEstimator
from app.ai.planner.scheduler import Scheduler
from app.ai.planner.optimizer import Optimizer
from app.ai.planner.validation import ValidationEngine
from app.ai.planner.recovery_planner import RecoveryPlanner
from app.ai.planner.workflow_generator import WorkflowGenerator
from app.ai.planner.context_builder import ContextBuilder
from app.ai.planner.memory import PlannerMemory
from app.ai.planner.cache import PlannerCache
from app.ai.planner.metrics import PlannerMetricsTracker

logger = structlog.get_logger("planner_engine")

class LocalPlannerEngine:
    """Consolidated orchestrator firing lifecycle events and caching workflow layouts."""

    def __init__(
        self,
        config: Optional[MultiAgentPlannerConfiguration] = None,
        registry: Optional[Any] = None,
        event_bus: Optional[Any] = None,
        memory_engine: Optional[Any] = None
    ) -> None:
        self.config = config or MultiAgentPlannerConfiguration()
        self.registry = registry
        self.event_bus = event_bus

        # Subsystems initialization
        self.analyzer = GoalAnalyzer()
        self.decomposition = DecompositionEngine()
        self.dag_builder = DAGBuilder()
        self.priority = PriorityEngine()
        self.matcher = CapabilityMatcher(self.registry)
        self.selector = AgentSelector(self.matcher)
        self.estimator = ExecutionEstimator()
        self.scheduler = Scheduler()
        self.optimizer = Optimizer()
        self.validator = ValidationEngine()
        self.recovery = RecoveryPlanner()
        self.context_builder = ContextBuilder()
        self.memory = PlannerMemory(memory_engine)
        self.cache = PlannerCache()
        self.metrics_tracker = PlannerMetricsTracker()

        # Build workflow scheduler optimizer generator
        self.workflow_generator = WorkflowGenerator(
            priority=self.priority,
            selector=self.selector,
            estimator=self.estimator,
            scheduler=self.scheduler,
            optimizer=self.optimizer,
            validator=self.validator,
            recovery=self.recovery
        )

    async def plan(self, request: PlanningRequest) -> PlanningResponse:
        """Executes the full sequences of planning stages, raising events on progress."""
        self.metrics_tracker.reset()
        self.metrics_tracker.start_stage("total")

        # Check Cache
        if not request.force_replanning:
            cached_plan = self.cache.get(request.goal)
            if cached_plan:
                logger.info("Found cached planning response", goal=request.goal)
                return cached_plan

        # Publish PlanningStarted
        if self.event_bus:
            await self.event_bus.publish("PlanningStarted", goal=request.goal)

        goal = Goal(
            goal_id=request.request_id,
            description=request.goal,
            context=request.context
        )

        try:
            # 2. Goal Analysis
            self.metrics_tracker.start_stage("analysis")
            analysis = await self.analyzer.analyze_goal(goal)
            self.metrics_tracker.end_stage("analysis")
            if self.event_bus:
                await self.event_bus.publish("GoalAnalyzed", goal_id=request.request_id)

            # 3. Task Decomposition
            self.metrics_tracker.start_stage("decomposition")
            task_tree = await self.decomposition.decompose(goal, analysis)
            self.metrics_tracker.end_stage("decomposition")
            if self.event_bus:
                await self.event_bus.publish("TasksCreated", goal_id=request.request_id)

            # 4. Dependency Graph Generation (DAG)
            self.metrics_tracker.start_stage("dag")
            dependency_graph = self.dag_builder.build_dag(task_tree)
            self.metrics_tracker.end_stage("dag")
            if self.event_bus:
                await self.event_bus.publish("DAGGenerated", goal_id=request.request_id)

            # 5. Workflow Generation (Batch scheduler, priority paths, agents select, estimations)
            self.metrics_tracker.start_stage("workflow")
            execution_plan = self.workflow_generator.generate_workflow(task_tree, dependency_graph)
            self.metrics_tracker.end_stage("workflow")
            if self.event_bus:
                await self.event_bus.publish("WorkflowCreated", goal_id=request.request_id)

            self.metrics_tracker.end_stage("total")
            timings = self.metrics_tracker.latencies

            # Compile planner metrics
            metrics = PlanningMetrics(
                planning_latency_ms=timings.get("total", 0.0),
                decomposition_depth=int(analysis.get("complexity", 0.5) * 5),
                task_count=task_tree.total_nodes,
                dag_size=len(dependency_graph.nodes),
                optimization_ratio=1.0
            )

            response = PlanningResponse(
                session_id=request.request_id,
                status="success",
                task_tree=task_tree,
                dependency_graph=dependency_graph,
                execution_plan=execution_plan,
                metrics=metrics
            )

            # Archive plan summary in long term index memory database
            plan_summary = f"Plan contains {len(execution_plan.batches)} batches, total seconds estimated: {execution_plan.total_estimated_seconds}"
            await self.memory.store_plan(request.request_id, request.goal, plan_summary)

            if self.event_bus:
                await self.event_bus.publish("PlanningCompleted", goal_id=request.request_id)

            # Save in Cache
            self.cache.set(request.goal, response)
            return response

        except Exception as err:
            self.metrics_tracker.end_stage("total")
            logger.error("Planning engine pipeline execution failed", request_id=request.request_id, error=str(err))

            if self.event_bus:
                await self.event_bus.publish("PlanningFailed", goal_id=request.request_id, error=str(err))

            # Return failed response containing empty structures
            empty_task = Task(task_id="empty", title="empty", description="empty")
            empty_tree = TaskTree(root_node=TaskNode(task=empty_task), total_nodes=0)
            empty_graph = DependencyGraph(nodes={}, edges=[])
            empty_plan = ExecutionPlan(plan_id="empty", batches=[], recovery_plans={}, total_estimated_seconds=0.0)

            return PlanningResponse(
                session_id=request.request_id,
                status="failed",
                task_tree=empty_tree,
                dependency_graph=empty_graph,
                execution_plan=empty_plan,
                metrics=PlanningMetrics(),
                error_message=str(err)
            )

    async def shutdown(self) -> None:
        """Teardown method to satisfy framework diagnostics checks."""
        pass
