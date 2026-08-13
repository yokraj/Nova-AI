"""WebSocket Security Manager Module.

Enforces connection limits per IP/user, max frame message size limits,
spam and flood detection algorithms, and abusive connection termination.
"""

from collections import defaultdict, deque
import time
from typing import Dict, List, Optional, Set
import structlog

from app.security.exceptions import WebSocketSecurityException

logger = structlog.get_logger(__name__)


class WebSocketSecurityManager:
    """Enterprise WebSocket Security & Anti-Abuse Enforcement Manager."""

    def __init__(
        self,
        max_message_size_bytes: int = 65536,
        max_connections_per_ip: int = 10,
        spam_threshold_per_5s: int = 20,
    ) -> None:
        self.max_message_size = max_message_size_bytes
        self.max_connections_per_ip = max_connections_per_ip
        self.spam_threshold = spam_threshold_per_5s

        self._message_timestamps: Dict[str, deque] = defaultdict(deque)
        logger.info("websocket_security_manager_initialized", max_size=max_message_size_bytes, max_conn_per_ip=max_connections_per_ip)

    def validate_connection(self, ip_address: str, active_connections_count: int) -> bool:
        """Validates if IP address has exceeded max connection limit."""
        if active_connections_count >= self.max_connections_per_ip:
            logger.warning("websocket_conn_limit_exceeded", ip=ip_address, count=active_connections_count)
            raise WebSocketSecurityException(f"Connection limit of {self.max_connections_per_ip} reached for IP {ip_address}.")
        return True

    def validate_channel_access(self, user_permissions: Set[str], channel: str) -> bool:
        """Validates if user RBAC permissions authorize subscribing to target channel."""
        # Admin permission bypasses channel checks
        if "dashboard:admin" in user_permissions or "admin:access" in user_permissions:
            return True

        channel_perm_map = {
            "dashboard": "dashboard:read",
            "system": "dashboard:metrics:read",
            "resources": "dashboard:metrics:read",
            "cpu": "dashboard:metrics:read",
            "memory": "dashboard:metrics:read",
            "disk": "dashboard:metrics:read",
            "gpu": "dashboard:metrics:read",
            "health": "dashboard:read",
            "notifications": "dashboard:read",
            "events": "dashboard:events:read",
            "logs": "dashboard:logs:read",
            "configuration": "dashboard:config:write",
        }

        required_perm = channel_perm_map.get(channel, "dashboard:read")
        if required_perm in user_permissions:
            return True

        # General read access allows basic dashboard read channels
        if channel in ["dashboard", "health", "notifications"] and ("dashboard:read" in user_permissions or "dashboard:overview:read" in user_permissions):
            return True

        logger.warning("websocket_channel_forbidden", channel=channel)
        return False

    def enforce_message_size(self, raw_payload_bytes: bytes) -> bool:
        """Enforces max allowed payload frame size."""
        if len(raw_payload_bytes) > self.max_message_size:
            logger.warning("websocket_message_size_exceeded", size=len(raw_payload_bytes), max_size=self.max_message_size)
            raise WebSocketSecurityException(f"Payload size {len(raw_payload_bytes)} bytes exceeds maximum {self.max_message_size} limit.")
        return True

    def detect_spam(self, ip_address: str) -> bool:
        """Detects if client IP is sending messages faster than spam threshold."""
        now = time.time()
        timestamps = self._message_timestamps[ip_address]
        cutoff = now - 5.0

        while timestamps and timestamps[0] < cutoff:
            timestamps.popleft()

        timestamps.append(now)
        if len(timestamps) > self.spam_threshold:
            logger.warning("websocket_spam_detected", ip=ip_address, count=len(timestamps))
            return True
        return False

    def detect_flooding(self, ip_address: str) -> bool:
        """Alias for detect_spam."""
        return self.detect_spam(ip_address)

    def terminate_abusive_connection(self, connection_id: str, reason: str) -> None:
        """Logs and flags abusive connection for termination."""
        logger.error("terminating_abusive_websocket", connection_id=connection_id, reason=reason)
