"""ArchitectAgent class inheriting from BaseAgent.
"""

from typing import Any, Dict, Optional
from app.ai.agents.base.base_agent import BaseAgent
from app.ai.agents.models import AgentMetadata
from app.agents.architect.workflow import ArchitectWorkflow

class ArchitectAgent(BaseAgent):
    """Specialized systems design and architecture specifications agent."""

    def __init__(self, metadata: AgentMetadata, config: Optional[Any] = None) -> None:
        super().__init__(metadata, config)
        self.workflow = ArchitectWorkflow(self.id)

    async def _on_execute(self, task: Any, **kwargs: Any) -> Dict[str, Any]:
        """Runs the design and planning execution logic."""
        params = task if isinstance(task, dict) else {"goal": str(task)}
        return await self.workflow.execute_design(self.session, params)
