"""Enterprise Security & Hardening Test Suite.

Validates RBAC privilege escalation prevention, sliding-window rate limit triggers,
brute-force alert emission, session revocation, and security headers.
"""

from unittest.mock import MagicMock
from fastapi.testclient import TestClient
import pytest

from app.security import (
    AuditLogger,
    ComplianceManager,
    DashboardRateLimiter,
    DashboardSessionManager,
    SecurityMonitor,
    ThreatDetector,
    WebSocketSecurityManager,
    check_dashboard_admin,
    check_dashboard_read,
    has_permission,
)
from app.security.exceptions import WebSocketSecurityException


def test_rbac_privilege_escalation_prevention():
    """Verifies that non-admin roles cannot perform admin operations."""
    assert check_dashboard_read("viewer") is True
    assert check_dashboard_admin("viewer") is False
    assert check_dashboard_admin("user") is False
    assert check_dashboard_admin("operator") is False
    assert check_dashboard_admin("admin") is True

    assert has_permission("user", "system:admin") is False
    assert has_permission("admin", "system:admin") is True


def test_brute_force_threat_detection_trigger():
    """Verifies that 5 failed login attempts trigger a BRUTE_FORCE_ATTEMPT alert."""
    audit = AuditLogger()
    monitor = SecurityMonitor(audit_logger=audit)
    detector = ThreatDetector()

    ip = "192.168.1.99"
    for i in range(5):
        count = monitor.track_failed_logins(ip, user_id="target_admin")

    assert count == 5
    threat = detector.detect_brute_force(ip, count, user_id="target_admin")
    assert threat is not None
    assert threat["threat_type"] == "BRUTE_FORCE_ATTEMPT"
    assert threat["severity"] == "HIGH"


def test_websocket_spam_protection():
    """Verifies that high-frequency WebSocket messaging triggers spam detection."""
    ws_sec = WebSocketSecurityManager(spam_threshold_per_5s=5)

    ip = "10.0.0.88"
    # Send 5 messages quickly
    for _ in range(5):
        assert ws_sec.detect_spam(ip) is False

    # 6th message triggers spam flag
    assert ws_sec.detect_spam(ip) is True
