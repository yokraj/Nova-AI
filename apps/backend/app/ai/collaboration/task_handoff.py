"""Task Handoff manager coordinating tasks transfers while preserving contexts.
"""

import structlog
import uuid
from typing import Dict, Any
from app.ai.collaboration.exceptions import HandoffError

logger = structlog.get_logger("task_handoff")

class TaskHandoff:
    """Handles task redirection handoffs between agents preserving execution history states."""

    def __init__(self) -> None:
        self.handoffs: Dict[str, Dict[str, Any]] = {}

    def initiate_handoff(self, task_id: str, from_agent: str, to_agent: str, context: Dict[str, Any]) -> str:
        """Saves execution context and begins handoff redirect."""
        handoff_id = str(uuid.uuid4())
        logger.info("Initiating task handoff redirection", handoff_id=handoff_id, task_id=task_id)
        self.handoffs[handoff_id] = {
            "task_id": task_id,
            "from_agent": from_agent,
            "to_agent": to_agent,
            "context": context,
            "status": "in_progress"
        }
        return handoff_id

    def complete_handoff(self, handoff_id: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Finalizes handoff process and resumes flow merging result parameters."""
        if handoff_id not in self.handoffs:
            raise HandoffError(f"Target handoff session not registered: {handoff_id}")

        record = self.handoffs[handoff_id]
        if record["status"] == "completed":
            raise HandoffError("Handoff session was already finalized")

        record["status"] = "completed"
        merged_context = {**record["context"], **results}
        logger.info("Task handoff completed successfully", handoff_id=handoff_id)
        return merged_context
