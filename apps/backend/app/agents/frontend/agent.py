"""FrontendAgent class inheriting from BaseAgent.
"""

from typing import Any, Dict, Optional
from app.ai.agents.base.base_agent import BaseAgent
from app.ai.agents.models import AgentMetadata
from app.agents.frontend.workflow import FrontendWorkflow

class FrontendAgent(BaseAgent):
    """Specialized React and client-side design layout dashboard builder agent."""

    def __init__(self, metadata: AgentMetadata, config: Optional[Any] = None) -> None:
        super().__init__(metadata, config)
        self.workflow = FrontendWorkflow(self.id)

    async def _on_execute(self, task: Any, **kwargs: Any) -> Dict[str, Any]:
        """Runs frontend components compile workflows."""
        params = task if isinstance(task, dict) else {"goal": str(task)}
        return await self.workflow.execute_frontend(self.session, params)
