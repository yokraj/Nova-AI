"""Unit tests for the Nova AI Gateway orchestration layer.

Verifies model registries, cost calculators, latency monitors, provider selection
policies, timeouts, and backoff retries behaviors.
"""

import asyncio
from typing import AsyncGenerator
import pytest

from app.ai import (
    AiGatewayService,
    BaseProvider,
    CostEstimator,
    GenerationRequest,
    GenerationResponse,
    HealthMonitor,
    InvalidModelException,
    ModelMetadata,
    ModelRegistry,
    PromptMessage,
    ProviderRateLimitException,
    ProviderRegistry,
    ProviderTimeoutException,
    StreamChunk,
    TokenUsage,
)


class MockProvider(BaseProvider):
    """Custom mock provider implementation for isolated gateway tests."""

    def __init__(self, name: str, supported_models: list[str]) -> None:
        self.name = name
        self.supported_models = supported_models
        self.calls_count = 0
        self.should_fail_times = 0
        self.should_timeout = False

    def get_name(self) -> str:
        return self.name

    async def generate_text(
        self, request: GenerationRequest
    ) -> GenerationResponse:
        self.calls_count += 1
        if self.should_fail_times > 0:
            self.should_fail_times -= 1
            raise Exception("Rate limit reached. HTTP 429 too many requests.")
        if self.should_timeout:
            await asyncio.sleep(0.5)  # Triggers gateway execution timeouts
        return GenerationResponse(
            content=f"Mock result from {self.name}",
            model=request.model,
            finish_reason="stop",
            usage=TokenUsage(
                prompt_tokens=100, completion_tokens=200, total_tokens=300
            ),
        )

    async def generate_stream(
        self, request: GenerationRequest
    ) -> AsyncGenerator[StreamChunk, None]:
        yield StreamChunk(content="Mock chunk delta.")
        yield StreamChunk(
            content="",
            finish_reason="stop",
            usage=TokenUsage(
                prompt_tokens=100, completion_tokens=200, total_tokens=300
            ),
        )

    def supports_model(self, model: str) -> bool:
        return model in self.supported_models

    def supports_capability(self, capability: str) -> bool:
        return capability == "text"


def test_registries_discovery() -> None:
    """Verifies that model metadata registers and discovers providers properly."""
    model_registry = ModelRegistry()
    provider_registry = ProviderRegistry()

    # Verify pre-registered models
    gpt = model_registry.get("gpt-4o")
    assert gpt is not None
    assert gpt.context_window == 128000

    # Register providers
    provider_a = MockProvider("OpenAI", ["gpt-4o"])
    provider_registry.register(provider_a)

    assert provider_registry.get("OpenAI") is provider_a
    assert provider_registry.select_for_model("gpt-4o") is provider_a
    assert provider_registry.select_for_model("claude-3-opus") is None


def test_cost_estimation_math() -> None:
    """Verifies precision cost estimation calculations."""
    model_registry = ModelRegistry()
    cost_estimator = CostEstimator(model_registry)

    # gpt-4o: input=$0.005/1K, output=$0.015/1K
    # prompt=2000 tokens ($0.01), completion=1000 tokens ($0.015). Total=$0.025
    cost = cost_estimator.calculate_cost("gpt-4o", 2000, 1000)
    assert cost == 0.025


def test_health_monitor_metrics() -> None:
    """Verifies that monitor calculates latency and error flags correctly."""
    health_monitor = HealthMonitor()
    health = health_monitor.get_health("TestProvider")

    assert health.is_healthy is True
    assert health.success_rate == 1.0

    # Record metrics
    health.record_success(150.0)
    health.record_success(250.0)
    assert health.average_latency_ms == 200.0

    # Record failures
    for _ in range(5):
        health.record_failure()
    assert health.success_rate < 0.5
    assert health.is_healthy is False


@pytest.mark.anyio
async def test_gateway_selection_and_generation() -> None:
    """Verifies standard successful text generation through gateway service."""
    model_registry = ModelRegistry()
    provider_registry = ProviderRegistry()
    cost_estimator = CostEstimator(model_registry)
    health_monitor = HealthMonitor()

    provider = MockProvider("OpenAI", ["gpt-4o"])
    provider_registry.register(provider)

    gateway = AiGatewayService(
        provider_registry=provider_registry,
        model_registry=model_registry,
        cost_estimator=cost_estimator,
        health_monitor=health_monitor,
        max_retries=2,
        timeout_seconds=5.0,
    )

    request = GenerationRequest(
        model="gpt-4o",
        messages=[PromptMessage(role="user", content="Hello")],
    )

    response = await gateway.generate_text(request)
    assert response.content == "Mock result from OpenAI"
    assert response.cost > 0.0
    assert provider.calls_count == 1


@pytest.mark.anyio
async def test_gateway_unsupported_model() -> None:
    """Verifies invalid model requests raise appropriate exceptions."""
    gateway = AiGatewayService(
        ProviderRegistry(),
        ModelRegistry(),
        CostEstimator(ModelRegistry()),
        HealthMonitor(),
    )
    request = GenerationRequest(
        model="unsupported", messages=[PromptMessage(role="user", content="Hi")]
    )
    with pytest.raises(InvalidModelException):
        await gateway.generate_text(request)


@pytest.mark.anyio
async def test_gateway_retry_and_backoff() -> None:
    """Verifies transient provider errors trigger retries and recover."""
    model_registry = ModelRegistry()
    provider_registry = ProviderRegistry()
    cost_estimator = CostEstimator(model_registry)
    health_monitor = HealthMonitor()

    provider = MockProvider("OpenAI", ["gpt-4o"])
    # Set to fail twice then succeed on third attempt
    provider.should_fail_times = 2
    provider_registry.register(provider)

    gateway = AiGatewayService(
        provider_registry=provider_registry,
        model_registry=model_registry,
        cost_estimator=cost_estimator,
        health_monitor=health_monitor,
        max_retries=3,
        timeout_seconds=5.0,
    )

    request = GenerationRequest(
        model="gpt-4o",
        messages=[PromptMessage(role="user", content="Test")],
    )

    response = await gateway.generate_text(request)
    assert response.content == "Mock result from OpenAI"
    assert provider.calls_count == 3  # Failed twice, succeeded on 3rd


@pytest.mark.anyio
async def test_gateway_max_retries_exceeded() -> None:
    """Verifies exhaustion of retries raises a rate limit exception."""
    model_registry = ModelRegistry()
    provider_registry = ProviderRegistry()

    provider = MockProvider("OpenAI", ["gpt-4o"])
    provider.should_fail_times = 5
    provider_registry.register(provider)

    gateway = AiGatewayService(
        provider_registry=provider_registry,
        model_registry=model_registry,
        cost_estimator=CostEstimator(model_registry),
        health_monitor=HealthMonitor(),
        max_retries=2,
        timeout_seconds=5.0,
    )

    request = GenerationRequest(
        model="gpt-4o",
        messages=[PromptMessage(role="user", content="Test")],
    )

    with pytest.raises(ProviderRateLimitException):
        await gateway.generate_text(request)


@pytest.mark.anyio
async def test_gateway_timeout_handling() -> None:
    """Verifies provider query execution timeouts are handled."""
    model_registry = ModelRegistry()
    provider_registry = ProviderRegistry()

    provider = MockProvider("OpenAI", ["gpt-4o"])
    provider.should_timeout = True
    provider_registry.register(provider)

    gateway = AiGatewayService(
        provider_registry=provider_registry,
        model_registry=model_registry,
        cost_estimator=CostEstimator(model_registry),
        health_monitor=HealthMonitor(),
        max_retries=1,
        timeout_seconds=0.1,  # Short timeout limit
    )

    request = GenerationRequest(
        model="gpt-4o",
        messages=[PromptMessage(role="user", content="Test")],
    )

    with pytest.raises(ProviderTimeoutException):
        await gateway.generate_text(request)
