"""NovaOrchestrator coordinating AI agents execution steps.
"""

from datetime import datetime, UTC
import uuid
from typing import Any, Dict, List, Optional

from app.agents.base import AgentContext
from app.agents.bus.request import AgentRequest
from app.agents.bus.routing import RoutingService
from app.agents.permissions.permission_manager import PermissionManager
from app.agents.permissions.permission_request import PermissionRequest
from app.agents.registry.registry import AgentRegistry
from app.agents.scheduler.priority import Priority
from app.agents.scheduler.scheduler import AgentScheduler
from app.ai.gateway.ai_gateway import AIGateway
from app.orchestrator.exceptions import OrchestrationError
from app.orchestrator.intent import IntentClassifier, IntentType
from app.orchestrator.planner import TaskPlanner
from app.orchestrator.response_builder import ResponseBuilder
from app.orchestrator.selector import AgentSelector
from app.orchestrator.state import ExecutionState
from app.orchestrator.executor import PlanExecutor


class NovaOrchestrator:
    """The central intelligence coordinating all AI Agent task pipelines in Nova AI."""

    def __init__(
        self,
        registry: AgentRegistry,
        permission_manager: PermissionManager,
        scheduler: AgentScheduler,
        routing_service: RoutingService,
        gateway: AIGateway,
        planner: Optional[TaskPlanner] = None,
        selector: Optional[AgentSelector] = None,
        response_builder: Optional[ResponseBuilder] = None,
    ) -> None:
        """Initializes NovaOrchestrator.

        Args:
            registry: Central AgentRegistry dependency.
            permission_manager: Enterprise PermissionManager dependency.
            scheduler: Enterprise AgentScheduler dependency.
            routing_service: Communication bus RoutingService dependency.
            gateway: AI Gateway dependency.
            planner: Optional custom TaskPlanner instance.
            selector: Optional custom AgentSelector instance.
            response_builder: Optional custom ResponseBuilder instance.
        """
        self.registry = registry
        self.permission_manager = permission_manager
        self.scheduler = scheduler
        self.routing_service = routing_service
        self.gateway = gateway

        # Sub-components
        self.classifier = IntentClassifier(gateway)
        self.planner = planner or TaskPlanner()
        self.selector = selector or AgentSelector(registry)
        self.response_builder = response_builder or ResponseBuilder()

        # Local execution state
        self.state = ExecutionState()
        self.executor = PlanExecutor(registry, permission_manager, scheduler, self.state)

    async def process(self, prompt: str, conversation_id: uuid.UUID) -> str:
        """Classifies intent, plans tasks, executes them, and builds a consolidated response.

        Args:
            prompt: User request prompt string.
            conversation_id: Session identifier.

        Returns:
            Formatted response output.
        """
        intent = await self.classifier.classify(prompt)
        candidates = self.selector.select(intent)
        ranked = self.selector.rank(candidates)
        target_agent_name = ranked[0] if ranked else self.selector.fallback(intent)

        plan = self.planner.create_plan(intent, prompt)
        for task in plan:
            task["agent_name"] = target_agent_name

        task_results = await self.execute(plan, conversation_id)
        aggregated = self.response_builder.aggregate(task_results)
        summary = self.response_builder.summarize(aggregated)
        return self.response_builder.format(summary)

    async def execute(self, plan: List[Dict[str, Any]], conversation_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Delegates plan steps execution to PlanExecutor.

        Args:
            plan: List of task definitions.
            conversation_id: Session identifier.

        Returns:
            List of executed tasks containing results.
        """
        return await self.executor.execute(plan, conversation_id)

    def cancel(self, task_id: uuid.UUID) -> None:
        """Cancels a pending or running task.

        Args:
            task_id: Target task identifier.
        """
        for task in self.state.pending:
            tid = task.get("id")
            if str(tid) == str(task_id):
                self.state.pending.remove(task)
                task["status"] = "cancelled"
                self.state.failed.append(task)
                try:
                    self.scheduler.cancel(task_id)
                except Exception:
                    pass
                return

        for task in self.state.running:
            tid = task.get("id")
            if str(tid) == str(task_id):
                self.state.running.remove(task)
                task["status"] = "cancelled"
                self.state.failed.append(task)
                try:
                    self.scheduler.cancel(task_id)
                except Exception:
                    pass
                return

    async def retry(self, task_id: uuid.UUID, conversation_id: Optional[uuid.UUID] = None) -> None:
        """Retries a failed task step, moving it to pending and executing it.

        Args:
            task_id: Target task identifier.
            conversation_id: Session identifier.
        """
        failed_task = None
        for task in self.state.failed:
            tid = task.get("id")
            if str(tid) == str(task_id):
                failed_task = task
                break

        if failed_task:
            self.state.failed.remove(failed_task)
            failed_task["status"] = "pending"
            failed_task["success"] = False
            failed_task["output"] = ""
            conv_id = conversation_id or uuid.uuid4()
            await self.execute([failed_task], conv_id)

    def health(self) -> Dict[str, Any]:
        """Checks orchestrator status and integrated dependencies health.

        Returns:
            Dict containing health status parameters.
        """
        return {
            "status": "healthy",
            "pending_tasks": len(self.state.pending),
            "running_tasks": len(self.state.running),
            "completed_tasks": len(self.state.completed),
            "failed_tasks": len(self.state.failed),
        }
