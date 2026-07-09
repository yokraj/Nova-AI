"""Central AI Gateway orchestration service for Nova AI.

Coordinates model execution across registered providers, managing retries,
timeouts, error transformations, cost metric lookups, and latency tracking.
"""

import asyncio
import time
from typing import AsyncGenerator, Optional
import structlog

from app.ai.exceptions import (
    AiGatewayException,
    InvalidModelException,
    normalize_provider_error,
)
from app.ai.cost import CostEstimator
from app.ai.health import HealthMonitor
from app.ai.models import GenerationRequest, GenerationResponse, StreamChunk
from app.ai.registry import ModelRegistry, ProviderRegistry

logger = structlog.get_logger(__name__)


class AiGatewayService:
    """Orchestrates structured, provider-independent text and streaming generation."""

    def __init__(
        self,
        provider_registry: ProviderRegistry,
        model_registry: ModelRegistry,
        cost_estimator: CostEstimator,
        health_monitor: HealthMonitor,
        default_model: str = "gpt-4o",
        max_retries: int = 3,
        timeout_seconds: float = 30.0,
    ) -> None:
        """Initializes the AiGatewayService.

        Args:
            provider_registry: Active registry matching provider instances.
            model_registry: Registry containing model metadata values.
            cost_estimator: Cost tracking estimator wrapper.
            health_monitor: Availability and latency metrics diagnostics.
            default_model: Name of default model to select if none specified.
            max_retries: Limit of execution retries on transient errors.
            timeout_seconds: Max query runtime limit before raising timeouts.
        """
        self.provider_registry = provider_registry
        self.model_registry = model_registry
        self.cost_estimator = cost_estimator
        self.health_monitor = health_monitor
        self.default_model = default_model
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds

    async def generate_text(
        self, request: GenerationRequest
    ) -> GenerationResponse:
        """Runs generation request inside a retry and timeout validation shell.

        Args:
            request: Configuration parameters payload.

        Returns:
            The output GenerationResponse metadata object.

        Raises:
            AiGatewayException: If attempts fail or rates throttling occurs.
        """
        model = request.model or self.default_model
        provider = self.provider_registry.select_for_model(model)

        if not provider:
            raise InvalidModelException(
                f"No provider registered supporting model: '{model}'"
            )

        provider_name = provider.get_name()
        health = self.health_monitor.get_health(provider_name)

        last_exception: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 1):
            start_time = time.perf_counter()
            try:
                # Wrap generation inside timeout executor
                response = await asyncio.wait_for(
                    provider.generate_text(request),
                    timeout=self.timeout_seconds,
                )
                latency_ms = (time.perf_counter() - start_time) * 1000
                health.record_success(latency_ms)

                # Track metrics and compute cost
                cost = self.cost_estimator.track_metrics(
                    provider=provider_name,
                    model=model,
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                )
                response.cost = cost
                return response

            except Exception as error:
                health.record_failure()
                last_exception = normalize_provider_error(provider_name, error)
                logger.warn(
                    "provider_call_failed",
                    provider=provider_name,
                    model=model,
                    attempt=attempt,
                    error=str(last_exception),
                )
                if attempt < self.max_retries:
                    # Exponential backoff delay
                    await asyncio.sleep(2**attempt * 0.1)

        raise last_exception or AiGatewayException(
            "Generation workflow failed."
        )

    async def generate_stream(
        self, request: GenerationRequest
    ) -> AsyncGenerator[StreamChunk, None]:
        """Runs stream token generation request delta chunk mappings.

        Args:
            request: Configuration parameters payload.

        Yields:
            StreamChunk delta increments.

        Raises:
            AiGatewayException: On streaming failures.
        """
        model = request.model or self.default_model
        provider = self.provider_registry.select_for_model(model)

        if not provider:
            raise InvalidModelException(
                f"No provider registered supporting model: '{model}'"
            )

        provider_name = provider.get_name()

        try:
            generator = await provider.generate_stream(request)
            async for chunk in generator:
                if chunk.usage:
                    # Register stats on the final telemetry chunk
                    self.cost_estimator.track_metrics(
                        provider=provider_name,
                        model=model,
                        prompt_tokens=chunk.usage.prompt_tokens,
                        completion_tokens=chunk.usage.completion_tokens,
                    )
                yield chunk
        except Exception as error:
            normalized = normalize_provider_error(provider_name, error)
            logger.error(
                "provider_stream_failed",
                provider=provider_name,
                model=model,
                error=str(normalized),
            )
            raise normalized
