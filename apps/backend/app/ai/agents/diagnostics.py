"""Diagnostics system archiving system-wide failures and lifecycles audits.
"""

from datetime import datetime
from typing import Dict, Any, List

class AgentDiagnostics:
    """Manages history records for troubleshooting and health auditing."""

    def __init__(self) -> None:
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.lifecycle_log: List[Dict[str, Any]] = []

    def record_error(self, message: str, details: str = "", category: str = "general") -> None:
        """Appends error entry with metadata context."""
        self.errors.append({
            "timestamp": datetime.utcnow(),
            "message": message,
            "details": details,
            "category": category
        })

    def record_warning(self, message: str, details: str = "", category: str = "general") -> None:
        """Appends warning entry with metadata context."""
        self.warnings.append({
            "timestamp": datetime.utcnow(),
            "message": message,
            "details": details,
            "category": category
        })

    def record_lifecycle_event(self, agent_id: str, event_type: str, details: str = "") -> None:
        """Logs lifecycle transition event."""
        self.lifecycle_log.append({
            "timestamp": datetime.utcnow(),
            "agent_id": agent_id,
            "event": event_type,
            "details": details
        })
