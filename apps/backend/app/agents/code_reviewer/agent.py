"""CodeReviewerAgent class inheriting from BaseAgent.
"""

from typing import Any, Dict, Optional
from app.ai.agents.base.base_agent import BaseAgent
from app.ai.agents.models import AgentMetadata
from app.agents.code_reviewer.workflow import CodeReviewerWorkflow

class CodeReviewerAgent(BaseAgent):
    """Specialized code quality inspector and architectural compliance reviewer agent."""

    def __init__(self, metadata: AgentMetadata, config: Optional[Any] = None) -> None:
        super().__init__(metadata, config)
        self.workflow = CodeReviewerWorkflow(self.id)

    async def _on_execute(self, task: Any, **kwargs: Any) -> Dict[str, Any]:
        """Runs pull requests review checks workflows."""
        params = task if isinstance(task, dict) else {"goal": str(task)}
        return await self.workflow.execute_review(self.session, params)
