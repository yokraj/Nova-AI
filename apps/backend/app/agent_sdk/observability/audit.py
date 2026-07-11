"""AuditLogger managing security events and config audits.
"""

from datetime import datetime, timezone
import json
from typing import Any, Dict, List


class AuditLogger:
    """Logs security audit records."""

    def __init__(self) -> None:
        """Initializes AuditLogger."""
        self._audit_records: List[Dict[str, Any]] = []

    def record(self, action: str, details: Dict[str, Any], user_id: str = "user") -> None:
        """Saves a security record payload.

        Args:
            action: Category or type of event.
            details: Context details dict.
            user_id: Active user identifier.
        """
        record_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "user_id": user_id,
            "details": details,
        }
        self._audit_records.append(record_entry)
        print(f"[AUDIT] {json.dumps(record_entry)}")

    def permission_change(self, agent_name: str, resource: str, action: str, effect: str) -> None:
        self.record(
            "permission_change",
            {"agent_name": agent_name, "resource": resource, "action": action, "effect": effect},
        )

    def configuration_change(self, component: str, key: str, value: Any) -> None:
        self.record("configuration_change", {"component": component, "key": key, "value": value})

    def agent_execution(self, agent_name: str, execution_id: str, success: bool) -> None:
        self.record("agent_execution", {"agent_name": agent_name, "execution_id": execution_id, "success": success})

    def security_event(self, event_type: str, severity: str, details: str) -> None:
        self.record("security_event", {"event_type": event_type, "severity": severity, "details": details})

    def list_records(self) -> List[Dict[str, Any]]:
        """Returns all recorded audits.

        Returns:
            List of recorded audits.
        """
        return self._audit_records
