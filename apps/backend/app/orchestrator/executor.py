"""PlanExecutor delegating task execution to scheduler and permission layers.
"""

from typing import Any, Dict, List
import uuid

from app.agents.bus.request import AgentRequest
from app.agents.permissions.permission_manager import PermissionManager
from app.agents.permissions.permission_request import PermissionRequest
from app.agents.registry.registry import AgentRegistry
from app.agents.scheduler.priority import Priority
from app.agents.scheduler.scheduler import AgentScheduler
from app.orchestrator.state import ExecutionState


class PlanExecutor:
    """Handles execution of planned tasks through permission and scheduling layers."""

    def __init__(
        self,
        registry: AgentRegistry,
        permission_manager: PermissionManager,
        scheduler: AgentScheduler,
        state: ExecutionState,
    ) -> None:
        """Initializes PlanExecutor.

        Args:
            registry: Active AgentRegistry.
            permission_manager: Active PermissionManager.
            scheduler: Active AgentScheduler.
            state: State tracking model to update.
        """
        self.registry = registry
        self.permission_manager = permission_manager
        self.scheduler = scheduler
        self.state = state

    async def execute(self, plan: List[Dict[str, Any]], conversation_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Executes plan steps, validating permissions and routing through scheduler.

        Args:
            plan: List of task definitions.
            conversation_id: Session identifier.

        Returns:
            List of executed tasks containing results.
        """
        self.state.pending = list(plan)
        results = []

        while self.state.pending:
            task = self.state.pending.pop(0)
            self.state.running.append(task)

            agent_name = task.get("agent_name", "ChatAgent")
            prompt = task.get("prompt", "")

            # 1. Resolve agent
            agent_id = None
            descriptor = None
            for d in self.registry.list():
                if d.name == agent_name:
                    agent_id = d.id
                    descriptor = d
                    break

            if not agent_id or not descriptor:
                task["success"] = False
                task["output"] = f"Agent '{agent_name}' not resolved in registry."
                self.state.running.remove(task)
                self.state.failed.append(task)
                results.append(task)
                continue

            # 2. Permission check
            permissions_allowed = True
            for perm in descriptor.permissions:
                try:
                    if not self.permission_manager.check_permission(agent_id, perm, "*"):
                        req = PermissionRequest(
                            agent_id=agent_id,
                            permission=perm,
                            resource="*",
                            reason="Orchestrator coordination check",
                        )
                        self.permission_manager.request_permission(req)
                except Exception as pe:
                    permissions_allowed = False
                    task["success"] = False
                    task["output"] = f"Permission check failed for agent '{agent_name}': {str(pe)}"
                    break

            if not permissions_allowed:
                self.state.running.remove(task)
                self.state.failed.append(task)
                results.append(task)
                continue

            # 3. Execution routing
            try:
                agent_request = AgentRequest(
                    sender="Orchestrator",
                    receiver=agent_name,
                    conversation_id=conversation_id,
                    payload={"prompt": prompt},
                )

                job = self.scheduler.submit(
                    agent_id=agent_id,
                    request=agent_request,
                    priority=Priority.NORMAL,
                )

                job_result = await self.scheduler.execute(job)

                if job_result.success:
                    task["success"] = True
                    task["output"] = job_result.output.get("response", "") if job_result.output else ""
                    self.state.running.remove(task)
                    self.state.completed.append(task)
                else:
                    task["success"] = False
                    task["output"] = "\n".join(job_result.errors)
                    self.state.running.remove(task)
                    self.state.failed.append(task)
            except Exception as e:
                task["success"] = False
                task["output"] = str(e)
                self.state.running.remove(task)
                self.state.failed.append(task)

            results.append(task)

        return results
