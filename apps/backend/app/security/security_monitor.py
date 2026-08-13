"""Security Monitor Module.

Monitors real-time security anomalies, tracks failed login attempts, permission failures,
rate-limit breaches, invalid token claims, WebSocket abuse, and generates security alerts.
"""

from collections import defaultdict
from datetime import datetime, timezone
import time
from typing import Any, Dict, List, Optional
import structlog

from app.security.audit_logger import AuditLogger

logger = structlog.get_logger(__name__)


class SecurityMonitor:
    """Enterprise Security Anomaly & Violation Monitor."""

    def __init__(self, audit_logger: Optional[AuditLogger] = None) -> None:
        self.audit_logger = audit_logger or AuditLogger()

        self._failed_logins: Dict[str, List[float]] = defaultdict(list)
        self._permission_failures: Dict[str, List[float]] = defaultdict(list)
        self._rate_limit_hits: Dict[str, List[float]] = defaultdict(list)
        self._invalid_tokens: Dict[str, List[float]] = defaultdict(list)
        self._suspicious_events: List[Dict[str, Any]] = []

        logger.info("security_monitor_initialized")

    def _cleanup_window(self, timestamps: List[float], window_seconds: float = 300.0) -> List[float]:
        """Evicts timestamps older than sliding window."""
        now = time.time()
        return [ts for ts in timestamps if (now - ts) <= window_seconds]

    def track_failed_logins(self, ip_address: str, user_id: Optional[str] = None) -> int:
        """Tracks a failed authentication attempt."""
        now = time.time()
        self._failed_logins[ip_address] = self._cleanup_window(self._failed_logins[ip_address])
        self._failed_logins[ip_address].append(now)

        count = len(self._failed_logins[ip_address])
        logger.warning("security_failed_login_tracked", ip=ip_address, user_id=user_id, count=count)

        if count >= 5:
            self.generate_security_alert("BRUTE_FORCE_ATTEMPT", {"ip": ip_address, "count": count})
        return count

    def track_permission_failures(self, ip_address: str, user_id: Optional[str] = None, permission: str = "") -> int:
        """Tracks an unauthorized access attempt."""
        now = time.time()
        self._permission_failures[ip_address] = self._cleanup_window(self._permission_failures[ip_address])
        self._permission_failures[ip_address].append(now)

        count = len(self._permission_failures[ip_address])
        self.audit_logger.log_permission_denied(user_id=user_id, role="unknown", ip_address=ip_address, endpoint="permission_check", required_permission=permission)

        if count >= 10:
            self.generate_security_alert("PERMISSION_SCANNING", {"ip": ip_address, "permission": permission, "count": count})
        return count

    def track_rate_limits(self, ip_address: str, endpoint: str) -> int:
        """Tracks a rate limit breach event."""
        now = time.time()
        self._rate_limit_hits[ip_address] = self._cleanup_window(self._rate_limit_hits[ip_address])
        self._rate_limit_hits[ip_address].append(now)

        count = len(self._rate_limit_hits[ip_address])
        logger.warning("security_rate_limit_tracked", ip=ip_address, endpoint=endpoint, count=count)
        return count

    def track_invalid_tokens(self, ip_address: str) -> int:
        """Tracks an invalid or expired JWT token presentation."""
        now = time.time()
        self._invalid_tokens[ip_address] = self._cleanup_window(self._invalid_tokens[ip_address])
        self._invalid_tokens[ip_address].append(now)

        count = len(self._invalid_tokens[ip_address])
        if count >= 5:
            self.generate_security_alert("TOKEN_ABUSE", {"ip": ip_address, "count": count})
        return count

    def track_suspicious_activity(self, ip_address: str, reason: str) -> None:
        """Tracks arbitrary suspicious activity events."""
        event = {"ip": ip_address, "reason": reason, "timestamp": datetime.now(timezone.utc).isoformat()}
        self._suspicious_events.append(event)
        self.audit_logger.log_security_event(threat_type="suspicious_activity", ip_address=ip_address, metadata={"reason": reason})

    def track_websocket_abuse(self, ip_address: str, reason: str) -> None:
        """Tracks WebSocket message spam or connection flood abuse."""
        self.generate_security_alert("WEBSOCKET_ABUSE", {"ip": ip_address, "reason": reason})

    def track_session_anomalies(self, user_id: str, reason: str) -> None:
        """Tracks session anomalies (e.g. concurrent login from different IPs)."""
        self.generate_security_alert("SESSION_ANOMALY", {"user_id": user_id, "reason": reason})

    def generate_security_alert(self, alert_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Emits a security alert event."""
        alert = {
            "alert_type": alert_type,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        logger.error("security_alert_generated", alert_type=alert_type, details=details)
        self.audit_logger.log_security_event(threat_type=alert_type, ip_address=details.get("ip", "127.0.0.1"), metadata=details)
        return alert

    def get_summary(self) -> Dict[str, Any]:
        """Returns security violation summary."""
        return {
            "failed_logins_count": sum(len(v) for v in self._failed_logins.values()),
            "permission_failures_count": sum(len(v) for v in self._permission_failures.values()),
            "rate_limit_hits_count": sum(len(v) for v in self._rate_limit_hits.values()),
            "invalid_tokens_count": sum(len(v) for v in self._invalid_tokens.values()),
            "suspicious_events_count": len(self._suspicious_events),
        }
