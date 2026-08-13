"""Nova AI Enterprise Dashboard Security & Hardening Package.

Provides audit logging, security monitoring, sliding-window rate limiting, session
management, WebSocket anti-abuse enforcement, threat detection, HTTP security headers,
extended RBAC permission helpers, compliance reports, and security middleware.
"""

from app.security.audit import AuditEvent
from app.security.audit_logger import AuditLogger
from app.security.compliance import ComplianceManager
from app.security.config import SecurityConfig
from app.security.exceptions import (
    AuditException,
    ComplianceException,
    RateLimitException,
    SecurityException,
    SessionExpiredException,
    ThreatDetectedException,
    WebSocketSecurityException,
)
from app.security.headers import apply_security_headers, get_security_headers
from app.security.middleware import DashboardSecurityMiddleware
from app.security.permissions import (
    check_analytics_read,
    check_dashboard_admin,
    check_dashboard_read,
    check_dashboard_write,
    check_notifications_read,
    check_notifications_write,
    check_system_admin,
    check_system_read,
    get_user_permissions,
    has_permission,
)
from app.security.rate_limiter import DashboardRateLimiter
from app.security.security_monitor import SecurityMonitor
from app.security.session_manager import DashboardSessionManager
from app.security.threat_detection import ThreatDetector
from app.security.websocket_security import WebSocketSecurityManager

__all__ = [
    "AuditLogger",
    "AuditEvent",
    "SecurityMonitor",
    "DashboardRateLimiter",
    "DashboardSessionManager",
    "WebSocketSecurityManager",
    "ThreatDetector",
    "ComplianceManager",
    "DashboardSecurityMiddleware",
    "SecurityConfig",
    "get_security_headers",
    "apply_security_headers",
    "has_permission",
    "get_user_permissions",
    "check_dashboard_read",
    "check_dashboard_write",
    "check_dashboard_admin",
    "check_analytics_read",
    "check_notifications_read",
    "check_notifications_write",
    "check_system_read",
    "check_system_admin",
    "SecurityException",
    "AuditException",
    "RateLimitException",
    "ThreatDetectedException",
    "SessionExpiredException",
    "WebSocketSecurityException",
    "ComplianceException",
]
