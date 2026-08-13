"""Security Configuration Module.

Defines configuration DTOs for enterprise dashboard security, rate limits, session TTLs,
WebSocket message limits, audit retention windows, and threat threshold triggers.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class SecurityConfig(BaseModel):
    """Configuration DTO for Dashboard Security & Hardening."""

    max_requests_per_minute: int = Field(default=120, ge=10, le=10000, description="Max API requests per minute per IP/user")
    burst_limit: int = Field(default=30, ge=5, le=500, description="Max burst requests within sliding window")
    session_ttl_seconds: int = Field(default=3600, ge=300, le=86400, description="Active session duration limit in seconds")
    max_ws_message_size: int = Field(default=65536, ge=1024, le=1048576, description="Max allowed WebSocket message size in bytes")
    max_ws_connections_per_ip: int = Field(default=10, ge=1, le=100, description="Max WebSocket connections allowed per client IP")
    audit_retention_days: int = Field(default=90, ge=7, le=3650, description="Days to retain security audit logs")
    failed_login_threshold: int = Field(default=5, ge=2, le=20, description="Consecutive failed logins before brute-force alert")
    spam_message_threshold: int = Field(default=20, ge=5, le=100, description="Max WebSocket messages per 5 seconds before spam alert")

    @classmethod
    def from_dashboard_config(cls, db_config: Optional[Any] = None) -> "SecurityConfig":
        """Instantiates SecurityConfig from DashboardConfiguration model or dict."""
        if not db_config:
            return cls()

        if isinstance(db_config, dict):
            return cls(
                max_requests_per_minute=int(db_config.get("max_requests_per_minute", 120)),
                burst_limit=int(db_config.get("burst_limit", 30)),
                session_ttl_seconds=int(db_config.get("session_ttl_seconds", 3600)),
                max_ws_message_size=int(db_config.get("max_ws_message_size", 65536)),
                max_ws_connections_per_ip=int(db_config.get("max_ws_connections_per_ip", 10)),
                audit_retention_days=int(db_config.get("audit_retention_days", 90)),
            )

        return cls(
            max_requests_per_minute=int(getattr(db_config, "max_requests_per_minute", 120)),
            burst_limit=int(getattr(db_config, "burst_limit", 30)),
            session_ttl_seconds=int(getattr(db_config, "session_ttl_seconds", 3600)),
            max_ws_message_size=int(getattr(db_config, "max_ws_message_size", 65536)),
            max_ws_connections_per_ip=int(getattr(db_config, "max_ws_connections_per_ip", 10)),
            audit_retention_days=int(getattr(db_config, "audit_retention_days", 90)),
        )
