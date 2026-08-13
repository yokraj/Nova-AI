"""Dashboard Security Middleware Module.

Central HTTP middleware applying security headers, audit logging, rate limiting,
request timing, and threat detection checks across all API endpoints.
"""

import time
from typing import Callable, Optional
from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
import structlog

from app.security.audit_logger import AuditLogger
from app.security.headers import apply_security_headers
from app.security.rate_limiter import DashboardRateLimiter
from app.security.security_monitor import SecurityMonitor
from app.security.threat_detection import ThreatDetector

logger = structlog.get_logger(__name__)


class DashboardSecurityMiddleware(BaseHTTPMiddleware):
    """Central Starlette Security & Hardening Middleware."""

    def __init__(
        self,
        app: Any,
        rate_limiter: Optional[DashboardRateLimiter] = None,
        audit_logger: Optional[AuditLogger] = None,
        security_monitor: Optional[SecurityMonitor] = None,
        threat_detector: Optional[ThreatDetector] = None,
    ) -> None:
        super().__init__(app)
        self.rate_limiter = rate_limiter or DashboardRateLimiter()
        self.audit_logger = audit_logger or AuditLogger()
        self.security_monitor = security_monitor or SecurityMonitor(audit_logger=self.audit_logger)
        self.threat_detector = threat_detector or ThreatDetector()

        logger.info("dashboard_security_middleware_initialized")

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        client_ip = request.client.host if request.client else "127.0.0.1"
        endpoint_path = request.url.path

        # 1. Rate Limiting Check
        rate_key = f"{client_ip}:{endpoint_path}"
        if not self.rate_limiter.allow_request(rate_key):
            count = self.security_monitor.track_rate_limits(client_ip, endpoint_path)
            self.threat_detector.detect_rate_limit_abuse(client_ip, count)
            self.audit_logger.log_permission_denied(
                user_id=None, role="unknown", ip_address=client_ip, endpoint=endpoint_path, required_permission="rate_limit"
            )
            response = Response(content='{"error": "RateLimitExceeded", "message": "Too many requests."}', status_code=status.HTTP_429_TOO_MANY_REQUESTS, media_type="application/json")
            return apply_security_headers(dict(response.headers))

        self.rate_limiter.record_request(rate_key)

        # 2. Execute Request Pipeline
        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = (time.time() - start_time) * 1000.0
            self.audit_logger.log_error(endpoint=endpoint_path, error_message=str(exc), ip_address=client_ip)
            raise

        duration_ms = (time.time() - start_time) * 1000.0
        response.headers["X-Process-Time-Ms"] = f"{duration_ms:.2f}"

        # 3. Apply HTTP Security Headers
        for k, v in apply_security_headers({}).items():
            response.headers[k] = v

        # 4. Audit Log API Access
        self.audit_logger.log_api_access(
            user_id=None,
            role="anonymous",
            ip_address=client_ip,
            endpoint=endpoint_path,
            action=request.method.lower(),
            resource="api",
            result="success" if response.status_code < 400 else "failure",
            metadata={"status_code": response.status_code, "duration_ms": round(duration_ms, 2)},
        )

        return response
