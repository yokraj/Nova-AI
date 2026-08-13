"""Service Metrics Tracker recording execution telemetry."""

import structlog

from app.ai.services.models import ServiceMetrics

logger = structlog.get_logger("service_metrics")


class ServiceMetricsTracker:
    """Tracks telemetry metrics for service automation platform."""

    def __init__(self) -> None:
        self._total = 0
        self._successes = 0
        self._failures = 0
        self._total_duration = 0.0
        self._travel_count = 0
        self._shopping_count = 0
        self._govt_count = 0
        self._finance_count = 0
        self._otp_count = 0

    def record_service(self, category: str) -> None:
        """Increment category counter."""
        self._total += 1
        if category == "travel":
            self._travel_count += 1
        elif category == "shopping":
            self._shopping_count += 1
        elif category == "government":
            self._govt_count += 1
        elif category == "finance":
            self._finance_count += 1

    def record_success(self, duration_seconds: float) -> None:
        """Record successful workflow."""
        self._successes += 1
        self._total_duration += duration_seconds

    def record_failure(self) -> None:
        """Record failed workflow."""
        self._failures += 1

    def get_metrics(self) -> ServiceMetrics:
        """Get metrics snapshot."""
        rate = (self._successes / self._total * 100.0) if self._total > 0 else 100.0
        avg_dur = (self._total_duration / self._successes) if self._successes > 0 else 0.0
        return ServiceMetrics(
            total_services_executed=self._total,
            successful_services=self._successes,
            failed_services=self._failures,
            success_rate=rate,
            average_duration_seconds=avg_dur,
            travel_workflows_count=self._travel_count,
            shopping_workflows_count=self._shopping_count,
            government_workflows_count=self._govt_count,
            finance_workflows_count=self._finance_count,
            otps_handled_count=self._otp_count,
        )
