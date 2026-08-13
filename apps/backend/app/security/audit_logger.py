"""Audit Logger Module.

Emits structured JSON security audit logs via structlog and maintains a bounded
in-memory ring buffer for compliance reporting and security audits.
"""

from collections import deque
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import structlog

from app.security.audit import AuditEvent

logger = structlog.get_logger("audit_logger")


class AuditLogger:
    """Enterprise Security Audit Logger."""

    def __init__(self, max_buffer_size: int = 5000) -> None:
        self.max_buffer_size = max_buffer_size
        self._buffer: deque = deque(maxlen=max_buffer_size)
        logger.info("audit_logger_initialized", max_buffer_size=max_buffer_size)

    def _emit(self, event: AuditEvent) -> AuditEvent:
        """Stores audit event in memory buffer and logs via structlog."""
        self._buffer.append(event)
        logger.info(
            "audit_event_logged",
            user_id=event.user_id,
            role=event.role,
            ip_address=event.ip_address,
            endpoint=event.endpoint,
            action=event.action,
            resource=event.resource,
            result=event.result,
        )
        return event

    def log_login(self, user_id: str, role: str, ip_address: str, result: str = "success", metadata: Optional[Dict[str, Any]] = None) -> AuditEvent:
        event = AuditEvent(
            user_id=user_id,
            role=role,
            ip_address=ip_address,
            endpoint="/api/v1/auth/login",
            action="login",
            resource="authentication",
            result=result,
            metadata=metadata or {},
        )
        return self._emit(event)

    def log_logout(self, user_id: str, role: str, ip_address: str, metadata: Optional[Dict[str, Any]] = None) -> AuditEvent:
        event = AuditEvent(
            user_id=user_id,
            role=role,
            ip_address=ip_address,
            endpoint="/api/v1/auth/logout",
            action="logout",
            resource="authentication",
            result="success",
            metadata=metadata or {},
        )
        return self._emit(event)

    def log_api_access(self, user_id: Optional[str], role: str, ip_address: str, endpoint: str, action: str, resource: str, result: str = "success", metadata: Optional[Dict[str, Any]] = None) -> AuditEvent:
        event = AuditEvent(
            user_id=user_id,
            role=role,
            ip_address=ip_address,
            endpoint=endpoint,
            action=action,
            resource=resource,
            result=result,
            metadata=metadata or {},
        )
        return self._emit(event)

    def log_websocket_connection(self, user_id: Optional[str], role: str, ip_address: str, action: str = "connect", result: str = "success", metadata: Optional[Dict[str, Any]] = None) -> AuditEvent:
        event = AuditEvent(
            user_id=user_id,
            role=role,
            ip_address=ip_address,
            endpoint="/ws/dashboard",
            action=action,
            resource="websocket_gateway",
            result=result,
            metadata=metadata or {},
        )
        return self._emit(event)

    def log_permission_denied(self, user_id: Optional[str], role: str, ip_address: str, endpoint: str, required_permission: str, metadata: Optional[Dict[str, Any]] = None) -> AuditEvent:
        meta = metadata or {}
        meta["required_permission"] = required_permission
        event = AuditEvent(
            user_id=user_id,
            role=role,
            ip_address=ip_address,
            endpoint=endpoint,
            action="permission_denied",
            resource="rbac_authorization",
            result="denied",
            metadata=meta,
        )
        return self._emit(event)

    def log_configuration_change(self, user_id: str, role: str, ip_address: str, setting_name: str, old_value: Any, new_value: Any) -> AuditEvent:
        event = AuditEvent(
            user_id=user_id,
            role=role,
            ip_address=ip_address,
            endpoint="/dashboard/config",
            action="update_config",
            resource="configuration",
            result="success",
            metadata={"setting": setting_name, "old_value": old_value, "new_value": new_value},
        )
        return self._emit(event)

    def log_notification_event(self, user_id: Optional[str], action: str, notification_id: str, metadata: Optional[Dict[str, Any]] = None) -> AuditEvent:
        meta = metadata or {}
        meta["notification_id"] = notification_id
        event = AuditEvent(
            user_id=user_id,
            role="user",
            ip_address="127.0.0.1",
            endpoint="/dashboard/notifications",
            action=action,
            resource="notification_engine",
            result="success",
            metadata=meta,
        )
        return self._emit(event)

    def log_security_event(self, threat_type: str, ip_address: str, user_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> AuditEvent:
        event = AuditEvent(
            user_id=user_id,
            role="unknown",
            ip_address=ip_address,
            endpoint="security_monitor",
            action=f"threat_{threat_type}",
            resource="threat_detector",
            result="alert",
            metadata=metadata or {},
        )
        return self._emit(event)

    def log_system_event(self, action: str, details: str, metadata: Optional[Dict[str, Any]] = None) -> AuditEvent:
        meta = metadata or {}
        meta["details"] = details
        event = AuditEvent(
            user_id="system",
            role="system",
            ip_address="127.0.0.1",
            endpoint="system_core",
            action=action,
            resource="system_engine",
            result="success",
            metadata=meta,
        )
        return self._emit(event)

    def log_error(self, endpoint: str, error_message: str, user_id: Optional[str] = None, ip_address: str = "127.0.0.1") -> AuditEvent:
        event = AuditEvent(
            user_id=user_id,
            role="unknown",
            ip_address=ip_address,
            endpoint=endpoint,
            action="error",
            resource="backend",
            result="error",
            metadata={"error": error_message},
        )
        return self._emit(event)

    def list_audit_events(self, limit: int = 100) -> List[AuditEvent]:
        """Returns most recent audit events."""
        return list(self._buffer)[-limit:]
