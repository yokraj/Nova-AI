"""StructuredLogger formatting logs to stdout in JSON format.
"""

from datetime import datetime, timezone
import json
from typing import Any, Dict, Optional
import uuid


class StructuredLogger:
    """Logs structured JSON parameters for frontend dashboard consumptions."""

    def __init__(self, agent_name: str) -> None:
        """Initializes StructuredLogger.

        Args:
            agent_name: Name of the agent.
        """
        self.agent_name = agent_name

    def _log(
        self,
        severity: str,
        message: str,
        execution_id: Optional[uuid.UUID] = None,
        request_id: Optional[uuid.UUID] = None,
        user_id: str = "user",
        conversation_id: Optional[uuid.UUID] = None,
        task_name: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Formats and prints JSON structured log dictionary."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "execution_id": str(execution_id) if execution_id else None,
            "request_id": str(request_id) if request_id else None,
            "user_id": user_id,
            "conversation_id": str(conversation_id) if conversation_id else None,
            "agent_name": self.agent_name,
            "task_name": task_name,
            "severity": severity,
            "message": message,
            "metadata": metadata or {},
        }
        print(json.dumps(entry))

    def debug(self, message: str, **kwargs: Any) -> None:
        self._log("DEBUG", message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        self._log("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        self._log("WARNING", message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        self._log("ERROR", message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        self._log("CRITICAL", message, **kwargs)

    def exception(self, message: str, **kwargs: Any) -> None:
        self._log("EXCEPTION", message, **kwargs)
