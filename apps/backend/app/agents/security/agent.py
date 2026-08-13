"""SecurityAgent class inheriting from BaseAgent.
"""

from typing import Any, Dict, Optional
from app.ai.agents.base.base_agent import BaseAgent
from app.ai.agents.models import AgentMetadata
from app.agents.security.workflow import SecurityWorkflow

class SecurityAgent(BaseAgent):
    """Specialized OWASP compliance auditor and credentials leaks scanner agent."""

    def __init__(self, metadata: AgentMetadata, config: Optional[Any] = None) -> None:
        super().__init__(metadata, config)
        self.workflow = SecurityWorkflow(self.id)

    async def _on_execute(self, task: Any, **kwargs: Any) -> Dict[str, Any]:
        """Runs security scans checks workflows."""
        params = task if isinstance(task, dict) else {"goal": str(task)}
        return await self.workflow.execute_security(self.session, params)
