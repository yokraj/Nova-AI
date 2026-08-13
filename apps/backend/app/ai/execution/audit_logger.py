"""Audit Logger logging security, approval, and action trails."""

from typing import Any, Dict
import structlog

logger = structlog.get_logger("execution_audit_logger")


class AuditLogger:
    """Logs structured audit trails for all executed actions, approvals, and security checks."""

    def log_action(self, mission_id: str, action: str, details: Dict[str, Any]) -> None:
        """Log an executed action."""
        logger.info(
            "AUDIT ACTION",
            mission_id=mission_id,
            action=action,
            details=details,
        )

    def log_approval(self, mission_id: str, capability: str, approved: bool) -> None:
        """Log a human approval decision."""
        logger.info(
            "AUDIT APPROVAL",
            mission_id=mission_id,
            capability=capability,
            approved=approved,
        )
