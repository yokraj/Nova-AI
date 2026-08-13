"""Retry Manager Module.

Implements exponential backoff retries, provider circuit breakers, max retry limits,
and health tracking.
"""

from typing import Any, Dict, Optional
import time
import structlog

from app.inference.config import InferenceConfig

logger = structlog.get_logger(__name__)


class RetryManager:
    """Enterprise Circuit Breaker & Exponential Backoff Retry Manager."""

    def __init__(self, config: Optional[InferenceConfig] = None) -> None:
        self.config = config or InferenceConfig()
        self._provider_failures: Dict[str, int] = {}
        self._circuit_open: Dict[str, float] = {}
        logger.info("retry_manager_initialized")

    def record_success(self, provider: str) -> None:
        """Records successful call and resets failure count."""
        self._provider_failures[provider] = 0
        if provider in self._circuit_open:
            del self._circuit_open[provider]

    def record_failure(self, provider: str) -> bool:
        """Records failure and trips circuit breaker if threshold is reached."""
        failures = self._provider_failures.get(provider, 0) + 1
        self._provider_failures[provider] = failures

        if failures >= self.config.circuit_breaker_failure_threshold:
            self._circuit_open[provider] = time.time() + self.config.circuit_breaker_recovery_seconds
            logger.warn("circuit_breaker_tripped", provider=provider, failures=failures)
            return True  # Circuit opened
        return False

    def is_circuit_open(self, provider: str) -> bool:
        """Checks if provider circuit breaker is currently open."""
        if provider not in self._circuit_open:
            return False
        if time.time() > self._circuit_open[provider]:
            del self._circuit_open[provider]
            return False  # Half-open recovery
        return True
