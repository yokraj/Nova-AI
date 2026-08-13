"""Compliance Manager Module.

Generates enterprise compliance reports including audit summaries, security reports,
permission matrices, active session reports, access history, and configuration change logs.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
import structlog

from app.security.audit_logger import AuditLogger
from app.security.permissions import EXTENDED_ROLE_PERMISSIONS
from app.security.security_monitor import SecurityMonitor
from app.security.session_manager import DashboardSessionManager

logger = structlog.get_logger(__name__)


class ComplianceManager:
    """Enterprise Compliance Report Generator."""

    def __init__(
        self,
        audit_logger: Optional[AuditLogger] = None,
        security_monitor: Optional[SecurityMonitor] = None,
        session_manager: Optional[DashboardSessionManager] = None,
    ) -> None:
        self.audit_logger = audit_logger or AuditLogger()
        self.security_monitor = security_monitor or SecurityMonitor(audit_logger=self.audit_logger)
        self.session_manager = session_manager or DashboardSessionManager()
        logger.info("compliance_manager_initialized")

    def _create_report_envelope(self, report_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Wraps compliance report data into standard envelope."""
        return {
            "report_id": str(uuid.uuid4()),
            "report_type": report_type,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "data": data,
        }

    def generate_audit_summary(self, limit: int = 100) -> Dict[str, Any]:
        """Generates audit logging activity summary report."""
        events = self.audit_logger.list_audit_events(limit=limit)
        actions_count: Dict[str, int] = {}
        for ev in events:
            act = ev.action
            actions_count[act] = actions_count.get(act, 0) + 1

        data = {
            "total_audit_events": len(events),
            "action_breakdown": actions_count,
            "recent_events": [ev.model_dump() for ev in events[:10]],
        }
        return self._create_report_envelope("Audit Trail Summary Report", data)

    def generate_security_report(self) -> Dict[str, Any]:
        """Generates security threats and violations report."""
        sec_summary = self.security_monitor.get_summary()
        return self._create_report_envelope("Enterprise Security & Threat Report", sec_summary)

    def generate_permission_report(self) -> Dict[str, Any]:
        """Generates RBAC permission matrix compliance report."""
        matrix = {role: list(perms) for role, perms in EXTENDED_ROLE_PERMISSIONS.items()}
        return self._create_report_envelope("RBAC Permission Matrix Report", {"roles": matrix})

    def generate_session_report(self) -> Dict[str, Any]:
        """Generates active user session report."""
        active_sessions = self.session_manager.list_active_sessions()
        data = {
            "active_sessions_count": len(active_sessions),
            "sessions": active_sessions,
        }
        return self._create_report_envelope("Active Sessions Compliance Report", data)

    def generate_access_report(self, limit: int = 100) -> Dict[str, Any]:
        """Generates API access and endpoint entry report."""
        events = [ev for ev in self.audit_logger.list_audit_events(limit=limit) if ev.action in ["login", "api_access", "connect"]]
        data = {
            "total_access_events": len(events),
            "access_log": [ev.model_dump() for ev in events],
        }
        return self._create_report_envelope("Endpoint Access History Report", data)

    def generate_config_history(self, limit: int = 100) -> Dict[str, Any]:
        """Generates configuration modification audit report."""
        events = [ev for ev in self.audit_logger.list_audit_events(limit=limit) if ev.resource == "configuration"]
        data = {
            "config_change_count": len(events),
            "changes": [ev.model_dump() for ev in events],
        }
        return self._create_report_envelope("Configuration Change Audit Report", data)
