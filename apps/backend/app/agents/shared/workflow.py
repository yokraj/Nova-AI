"""Shared workflow orchestrations for specialized agents execution runs.
"""

import structlog
from typing import Dict, Any
from app.ai.agents.base.agent_result import AgentResult
from app.ai.agents.base.agent_session import AgentSession

logger = structlog.get_logger("shared_specialist_workflow")

class BaseSpecialistWorkflow:
    """Executes actions and logs transitions inside active session histories."""

    def __init__(self, agent_id: str) -> None:
        self.agent_id = agent_id

    async def run(self, session: AgentSession, action: str, parameters: Dict[str, Any]) -> AgentResult:
        """Runs the workflow sequence, returning structured execution metrics."""
        logger.info("Initiated specialist execution workflow", agent_id=self.agent_id, action=action)
        session.record_state_change("READY", "BUSY", details=f"Started action execution: {action}")

        # Returns deterministic execution structures (overridden by sub-workflows)
        return AgentResult(
            success=True,
            data={
                "action": action,
                "parameters": parameters,
                "status": "completed"
            },
            metrics={"duration_ms": 10.0}
        )
