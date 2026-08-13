"""Mock Agent subclassing BaseAgent for test suites executions.
"""

import structlog
from typing import Any, Dict
from app.ai.agents.base.base_agent import BaseAgent
from app.ai.agents.models import AgentMetadata

logger = structlog.get_logger("mock_agent")

class MockAgent(BaseAgent):
    """Mock agent implementation returning deterministic execution dicts."""

    async def _on_execute(self, task: Any, **kwargs: Any) -> Dict[str, Any]:
        """Simulates processing a task, returning a success payload."""
        logger.info("Mock agent processing target task", task=task)
        return {
            "task_received": task,
            "status": "completed",
            "mock_result": f"Successfully completed: {str(task)}"
        }
