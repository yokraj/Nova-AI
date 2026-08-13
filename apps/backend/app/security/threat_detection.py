"""Threat Detection Module.

Identifies brute-force login attempts, rapid reconnects, token abuse, permission scanning,
rate-limit breaches, malformed payload attacks, and WebSocket flooding.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
import structlog

from app.security.exceptions import ThreatDetectedException

logger = structlog.get_logger(__name__)


class ThreatDetector:
    """Enterprise Threat & Intrusion Detection Engine."""

    def __init__(self) -> None:
        self._threat_history: List[Dict[str, Any]] = []
        logger.info("threat_detector_initialized")

    def _create_threat_event(self, threat_type: str, severity: str, ip_address: str, user_id: Optional[str], details: Dict[str, Any]) -> Dict[str, Any]:
        """Constructs a structured threat event DTO."""
        event = {
            "threat_id": str(uuid.uuid4()),
            "threat_type": threat_type,
            "severity": severity,
            "ip_address": ip_address,
            "user_id": user_id,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._threat_history.append(event)
        logger.error("threat_detected_alert", threat_type=threat_type, severity=severity, ip=ip_address, details=details)
        return event

    def detect_brute_force(self, ip_address: str, failed_count: int, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Detects brute-force authentication attempts."""
        if failed_count >= 5:
            return self._create_threat_event(
                threat_type="BRUTE_FORCE_ATTEMPT",
                severity="HIGH" if failed_count < 10 else "CRITICAL",
                ip_address=ip_address,
                user_id=user_id,
                details={"failed_login_count": failed_count},
            )
        return None

    def detect_rapid_reconnects(self, ip_address: str, reconnect_count: int) -> Optional[Dict[str, Any]]:
        """Detects rapid WebSocket reconnect storms."""
        if reconnect_count >= 10:
            return self._create_threat_event(
                threat_type="RAPID_RECONNECT_STORM",
                severity="HIGH",
                ip_address=ip_address,
                user_id=None,
                details={"reconnect_count": reconnect_count},
            )
        return None

    def detect_token_abuse(self, ip_address: str, invalid_token_count: int) -> Optional[Dict[str, Any]]:
        """Detects invalid or forged JWT token presentation."""
        if invalid_token_count >= 5:
            return self._create_threat_event(
                threat_type="TOKEN_FORGERY_ABUSE",
                severity="HIGH",
                ip_address=ip_address,
                user_id=None,
                details={"invalid_token_count": invalid_token_count},
            )
        return None

    def detect_permission_abuse(self, ip_address: str, denial_count: int, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Detects permission probing and endpoint scanning."""
        if denial_count >= 10:
            return self._create_threat_event(
                threat_type="PERMISSION_SCANNING",
                severity="CRITICAL",
                ip_address=ip_address,
                user_id=user_id,
                details={"denial_count": denial_count},
            )
        return None

    def detect_rate_limit_abuse(self, ip_address: str, rate_limit_count: int) -> Optional[Dict[str, Any]]:
        """Detects API rate-limit abuse."""
        if rate_limit_count >= 15:
            return self._create_threat_event(
                threat_type="RATE_LIMIT_ABUSE",
                severity="HIGH",
                ip_address=ip_address,
                user_id=None,
                details={"rate_limit_count": rate_limit_count},
            )
        return None

    def detect_invalid_payloads(self, ip_address: str, malformed_count: int) -> Optional[Dict[str, Any]]:
        """Detects repeated malformed or corrupt JSON payload submissions."""
        if malformed_count >= 10:
            return self._create_threat_event(
                threat_type="MALFORMED_PAYLOAD_ATTACK",
                severity="MEDIUM",
                ip_address=ip_address,
                user_id=None,
                details={"malformed_count": malformed_count},
            )
        return None

    def detect_websocket_flooding(self, ip_address: str, message_rate: float) -> Optional[Dict[str, Any]]:
        """Detects WebSocket payload message flooding."""
        if message_rate > 20.0:
            return self._create_threat_event(
                threat_type="WEBSOCKET_FLOODING",
                severity="CRITICAL",
                ip_address=ip_address,
                user_id=None,
                details={"message_rate_per_sec": message_rate},
            )
        return None

    def list_threats(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns list of detected threat events."""
        return self._threat_history[-limit:]
