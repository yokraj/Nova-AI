"""DevOpsAgent class inheriting from BaseAgent.
"""

from typing import Any, Dict, Optional
from app.ai.agents.base.base_agent import BaseAgent
from app.ai.agents.models import AgentMetadata
from app.agents.devops.workflow import DevOpsWorkflow

class DevOpsAgent(BaseAgent):
    """Specialized Docker compiler and GitHub Actions pipeline orchestrator agent."""

    def __init__(self, metadata: AgentMetadata, config: Optional[Any] = None) -> None:
        super().__init__(metadata, config)
        self.workflow = DevOpsWorkflow(self.id)

    async def _on_execute(self, task: Any, **kwargs: Any) -> Dict[str, Any]:
        """Runs devops deployments setups workflows."""
        params = task if isinstance(task, dict) else {"goal": str(task)}
        return await self.workflow.execute_devops(self.session, params)
