"""Health Checker drafts diagnostic script configurations.
"""

from typing import Dict, Any
from app.agents.software_engineer.deployment.models import HealthCheck

class LocalHealthChecker:
    """Manages endpoints check templates."""

    def generate_health_check_spec(self, endpoint: str = "/health") -> HealthCheck:
        """Returns standard HealthCheck model structure."""
        return HealthCheck(
            endpoint=endpoint,
            status="healthy",
            latency=12.5,
            rules={"http_code": 200, "body_contains": "status"},
        )
