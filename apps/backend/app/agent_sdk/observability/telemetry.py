"""TelemetryCollector tracking system resources.
"""

from typing import Any, Dict

from app.agent_sdk.observability.metrics import MetricsCollector


class TelemetryCollector:
    """Collects system, memory, and model usage snapshots."""

    def __init__(self) -> None:
        """Initializes TelemetryCollector."""
        self.metrics = MetricsCollector()

    def collect(self, cpu: float, memory: float, tokens: int = 0) -> None:
        """Records placeholder system usage.

        Args:
            cpu: CPU usage percent.
            memory: Memory usage in MB.
            tokens: Token counts.
        """
        self.metrics.cpu_usage = cpu
        self.metrics.memory_usage = memory
        self.metrics.token_usage += tokens

    def snapshot(self) -> Dict[str, Any]:
        """Captures a serializable state dictionary.

        Returns:
            Serializable metrics parameters.
        """
        return self.metrics.model_dump()

    def export(self) -> Dict[str, Any]:
        """Exports metrics payload.

        Returns:
            Metrics snapshot.
        """
        return self.snapshot()

    def reset(self) -> None:
        """Resets telemetry state variables."""
        self.metrics = MetricsCollector()
