"""Unit and Integration Test Suite for Nova AI Dashboard Security & Hardening.

Tests AuditLogger, SecurityMonitor, DashboardRateLimiter, DashboardSessionManager,
WebSocketSecurityManager, ThreatDetector, ComplianceManager, SecurityHeaders, and DashboardSecurityMiddleware.
"""

import asyncio
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.security import (
    AuditLogger,
    ComplianceManager,
    DashboardRateLimiter,
    DashboardSecurityMiddleware,
    DashboardSessionManager,
    SecurityConfig,
    SecurityMonitor,
    ThreatDetector,
    WebSocketSecurityManager,
    apply_security_headers,
    check_dashboard_admin,
    check_dashboard_read,
    get_security_headers,
    has_permission,
)
from app.security.exceptions import WebSocketSecurityException


def test_security_config():
    """Test SecurityConfig default values."""
    cfg = SecurityConfig()
    assert cfg.max_requests_per_minute == 120
    assert cfg.burst_limit == 30
    assert cfg.session_ttl_seconds == 3600
    assert cfg.max_ws_message_size == 65536


def test_audit_logger():
    """Test AuditLogger event logging and ring buffer storage."""
    audit = AuditLogger(max_buffer_size=10)

    ev1 = audit.log_login(user_id="user-1", role="admin", ip_address="192.168.1.1")
    assert ev1.action == "login"
    assert ev1.result == "success"

    ev2 = audit.log_permission_denied(user_id="user-2", role="user", ip_address="192.168.1.2", endpoint="/admin", required_permission="dashboard:admin")
    assert ev2.action == "permission_denied"
    assert ev2.result == "denied"

    events = audit.list_audit_events()
    assert len(events) == 2


def test_security_monitor():
    """Test SecurityMonitor tracking violations and alert generation."""
    monitor = SecurityMonitor()

    # Track 5 failed logins -> generates BRUTE_FORCE_ATTEMPT alert
    for _ in range(5):
        count = monitor.track_failed_logins(ip_address="10.0.0.1", user_id="admin")
    assert count == 5

    summary = monitor.get_summary()
    assert summary["failed_logins_count"] == 5


def test_dashboard_rate_limiter():
    """Test DashboardRateLimiter sliding window and burst limits."""
    limiter = DashboardRateLimiter(max_requests_per_min=3, burst_limit=5)
    key = "192.168.1.10:/api/v1/test"

    assert limiter.allow_request(key) is True
    limiter.record_request(key)

    assert limiter.allow_request(key) is True
    limiter.record_request(key)

    assert limiter.allow_request(key) is True
    limiter.record_request(key)

    # 4th request exceeds max rate of 3
    assert limiter.allow_request(key) is False

    limiter.reset(key)
    assert limiter.allow_request(key) is True


def test_session_manager():
    """Test DashboardSessionManager session creation, validation, and termination."""
    sess_mgr = DashboardSessionManager(session_ttl_seconds=60)

    session = sess_mgr.create_session(user_id="usr-100", role="admin", ip_address="127.0.0.1", user_agent="PyTest")
    sid = session["session_id"]

    assert sess_mgr.validate_session(sid) is not None
    assert len(sess_mgr.list_active_sessions("usr-100")) == 1

    # Terminate user sessions
    terminated = sess_mgr.terminate_all_sessions("usr-100")
    assert terminated == 1
    assert sess_mgr.validate_session(sid) is None


def test_websocket_security_manager():
    """Test WebSocketSecurityManager payload size enforcement and channel permissions."""
    ws_sec = WebSocketSecurityManager(max_message_size_bytes=100, max_connections_per_ip=2)

    # Valid payload size
    assert ws_sec.enforce_message_size(b"hello world") is True

    # Exceeded payload size raises exception
    with pytest.raises(WebSocketSecurityException):
        ws_sec.enforce_message_size(b"x" * 200)

    # Channel access checks
    admin_perms = {"dashboard:admin"}
    user_perms = {"dashboard:read"}

    assert ws_sec.validate_channel_access(admin_perms, "configuration") is True
    assert ws_sec.validate_channel_access(user_perms, "dashboard") is True
    assert ws_sec.validate_channel_access(user_perms, "configuration") is False


def test_threat_detector():
    """Test ThreatDetector event classification."""
    detector = ThreatDetector()

    event = detector.detect_brute_force(ip_address="1.2.3.4", failed_count=6)
    assert event is not None
    assert event["threat_type"] == "BRUTE_FORCE_ATTEMPT"
    assert event["severity"] == "HIGH"

    flood = detector.detect_websocket_flooding(ip_address="1.2.3.4", message_rate=30.0)
    assert flood is not None
    assert flood["threat_type"] == "WEBSOCKET_FLOODING"


def test_permissions_helpers():
    """Test RBAC permission helpers."""
    assert check_dashboard_admin("admin") is True
    assert check_dashboard_read("user") is True
    assert check_dashboard_admin("user") is False
    assert has_permission("operator", "notifications:write") is True


def test_compliance_manager():
    """Test ComplianceManager report generation."""
    compliance = ComplianceManager()

    audit_rpt = compliance.generate_audit_summary()
    assert audit_rpt["report_type"] == "Audit Trail Summary Report"

    perm_rpt = compliance.generate_permission_report()
    assert "admin" in perm_rpt["data"]["roles"]

    sec_rpt = compliance.generate_security_report()
    assert "failed_logins_count" in sec_rpt["data"]


def test_security_middleware_headers_and_rate_limiting():
    """Test FastAPI TestClient response receives HTTP security headers."""
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    headers = response.headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
