"""AI Provider health and latency diagnostics metrics for Nova AI Gateway.

Tracks response statuses, success/failure rates, and sample queries latency.
"""

from typing import Dict, List


class ProviderHealth:
    """Tracks latency and availability metrics for a registered AI provider."""

    def __init__(self) -> None:
        self.is_healthy: bool = True
        self.total_requests: int = 0
        self.failed_requests: int = 0
        self.latency_samples: List[float] = []

    @property
    def success_rate(self) -> float:
        """Returns the success rate ratio (0.0 to 1.0)."""
        if self.total_requests == 0:
            return 1.0
        return 1.0 - (self.failed_requests / self.total_requests)

    @property
    def average_latency_ms(self) -> float:
        """Returns the average latency in milliseconds for successful calls."""
        if not self.latency_samples:
            return 0.0
        return sum(self.latency_samples) / len(self.latency_samples)

    def record_success(self, latency_ms: float) -> None:
        """Records a successful provider call sample.

        Args:
            latency_ms: Query response duration in milliseconds.
        """
        self.total_requests += 1
        self.is_healthy = True
        self.latency_samples.append(latency_ms)
        # Keep sample metrics bounded to last 100 values
        if len(self.latency_samples) > 100:
            self.latency_samples.pop(0)

    def record_failure(self) -> None:
        """Records a failed provider call sample."""
        self.total_requests += 1
        self.failed_requests += 1
        # If success rates drop under 50% after initial calls, flag provider as unhealthy
        if self.total_requests >= 5 and self.success_rate < 0.5:
            self.is_healthy = False


class HealthMonitor:
    """Consolidates health metrics tracking for all registered providers."""

    def __init__(self) -> None:
        self.providers: Dict[str, ProviderHealth] = {}

    def get_health(self, provider_name: str) -> ProviderHealth:
        """Retrieves or initializes the health status tracker for a provider."""
        if provider_name not in self.providers:
            self.providers[provider_name] = ProviderHealth()
        return self.providers[provider_name]
