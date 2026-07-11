"""Unit tests for the Nova AI Gateway orchestration layers (Legacy and Enterprise V2).

Verifies model registries, cost calculators, latency monitors, provider selection,
timeouts, and backoff retries behaviors for both gateway versions.
"""

import asyncio
from typing import AsyncGenerator, List, Any
import pytest
from pydantic import ValidationError

# Legacy Gateway Imports
from app.ai import (
    AiGatewayService,
    BaseProvider,
    CostEstimator,
    GenerationRequest,
    GenerationResponse,
    HealthMonitor,
    InvalidModelException,
    ModelMetadata,
    ModelRegistry as LegacyModelRegistry,
    PromptMessage,
    ProviderRateLimitException,
    ProviderRegistry as LegacyProviderRegistry,
    ProviderTimeoutException,
    StreamChunk,
    TokenUsage,
)

# New Enterprise Gateway Imports
from app.ai.gateway import (
    AIGateway,
    ProviderRegistry,
    ModelRegistry,
    ProviderFactory,
    RetryPolicy,
    TimeoutPolicy,
    RequestContext,
    GatewayResponse,
    ProviderNotFoundError,
    ProviderUnavailableError,
    ModelUnavailableError,
    CapabilityUnavailableError,
    GatewayTimeoutError,
    GatewayConfig,
)
from app.ai.models import (
    ChatRequest,
    ChatResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    StreamingChunk,
    PromptMessage as PromptMessageContract,
    ProviderCapability,
    AIModelInfo,
    ModelType,
    FinishReason,
)
from app.ai.providers.contracts import (
    ILLMProvider,
    IEmbeddingProvider,
    IImageProvider,
    ISpeechProvider,
    IVisionProvider,
)


# ====================================================
# Legacy Mock Provider & Tests
# ====================================================
class LegacyMockProvider(BaseProvider):
    """Custom mock provider implementation for isolated legacy gateway tests."""

    def __init__(self, name: str, supported_models: List[str]) -> None:
        self.name = name
        self.supported_models = supported_models
        self.calls_count = 0
        self.should_fail_times = 0
        self.should_timeout = False

    def get_name(self) -> str:
        return self.name

    async def generate_text(self, request: GenerationRequest) -> GenerationResponse:
        self.calls_count += 1
        if self.should_fail_times > 0:
            self.should_fail_times -= 1
            raise Exception("Rate limit reached. HTTP 429 too many requests.")
        if self.should_timeout:
            await asyncio.sleep(0.5)
        return GenerationResponse(
            content=f"Mock result from {self.name}",
            model=request.model,
            finish_reason="stop",
            usage=TokenUsage(prompt_tokens=100, completion_tokens=200, total_tokens=300),
        )

    async def generate_stream(self, request: GenerationRequest) -> AsyncGenerator[StreamChunk, None]:
        yield StreamChunk(content=f"Chunk from {self.name}")

    def supports_model(self, model: str) -> bool:
        return model in self.supported_models

    def supports_capability(self, capability: str) -> bool:
        return capability == "text"


@pytest.mark.anyio
async def test_legacy_gateway_provider_routing() -> None:
    """Verifies that the legacy gateway resolves and routes calls to correct provider."""
    model_registry = LegacyModelRegistry()
    provider_registry = LegacyProviderRegistry()

    provider_openai = LegacyMockProvider("OpenAI", ["gpt-4o"])
    provider_anthropic = LegacyMockProvider("Anthropic", ["claude-3-opus"])

    provider_registry.register(provider_openai)
    provider_registry.register(provider_anthropic)

    gateway = AiGatewayService(
        provider_registry=provider_registry,
        model_registry=model_registry,
        cost_estimator=CostEstimator(model_registry),
        health_monitor=HealthMonitor(),
    )

    request = GenerationRequest(
        model="claude-3-opus",
        messages=[PromptMessage(role="user", content="Hi")],
    )

    response = await gateway.generate_text(request)
    assert response.content == "Mock result from Anthropic"
    assert provider_anthropic.calls_count == 1
    assert provider_openai.calls_count == 0


@pytest.mark.anyio
async def test_legacy_gateway_unsupported_model() -> None:
    """Verifies that selecting an unregistered model triggers InvalidModelException."""
    model_registry = LegacyModelRegistry()
    provider_registry = LegacyProviderRegistry()

    gateway = AiGatewayService(
        provider_registry=provider_registry,
        model_registry=model_registry,
        cost_estimator=CostEstimator(model_registry),
        health_monitor=HealthMonitor(),
    )

    request = GenerationRequest(
        model="non-existent-model",
        messages=[PromptMessage(role="user", content="Hi")],
    )

    with pytest.raises(InvalidModelException):
        await gateway.generate_text(request)


@pytest.mark.anyio
async def test_legacy_gateway_cost_accumulation() -> None:
    """Verifies correct calculation and assignment of monetary call cost metrics."""
    model_registry = LegacyModelRegistry()
    provider_registry = LegacyProviderRegistry()

    provider = LegacyMockProvider("OpenAI", ["gpt-4o"])
    provider_registry.register(provider)

    gateway = AiGatewayService(
        provider_registry=provider_registry,
        model_registry=model_registry,
        cost_estimator=CostEstimator(model_registry),
        health_monitor=HealthMonitor(),
    )

    request = GenerationRequest(
        model="gpt-4o",
        messages=[PromptMessage(role="user", content="Test")],
    )

    response = await gateway.generate_text(request)
    # prompt cost = 100 * (0.005 / 1000) = 0.0005
    # completion cost = 200 * (0.015 / 1000) = 0.003
    # total cost = 0.0035
    assert abs(response.cost - 0.0035) < 1e-6


@pytest.mark.anyio
async def test_legacy_gateway_retry_backoff() -> None:
    """Verifies gateway retries on transient errors and eventually succeeds."""
    model_registry = LegacyModelRegistry()
    provider_registry = LegacyProviderRegistry()

    provider = LegacyMockProvider("OpenAI", ["gpt-4o"])
    provider.should_fail_times = 2
    provider_registry.register(provider)

    gateway = AiGatewayService(
        provider_registry=provider_registry,
        model_registry=model_registry,
        cost_estimator=CostEstimator(model_registry),
        health_monitor=HealthMonitor(),
        max_retries=3,
        timeout_seconds=5.0,
    )

    request = GenerationRequest(
        model="gpt-4o",
        messages=[PromptMessage(role="user", content="Test")],
    )

    response = await gateway.generate_text(request)
    assert response.content == "Mock result from OpenAI"
    assert provider.calls_count == 3


@pytest.mark.anyio
async def test_legacy_gateway_max_retries_exceeded() -> None:
    """Verifies exhaustion of retries raises a rate limit exception."""
    model_registry = LegacyModelRegistry()
    provider_registry = LegacyProviderRegistry()

    provider = LegacyMockProvider("OpenAI", ["gpt-4o"])
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
async def test_legacy_gateway_timeout_handling() -> None:
    """Verifies provider query execution timeouts are handled."""
    model_registry = LegacyModelRegistry()
    provider_registry = LegacyProviderRegistry()

    provider = LegacyMockProvider("OpenAI", ["gpt-4o"])
    provider.should_timeout = True
    provider_registry.register(provider)

    gateway = AiGatewayService(
        provider_registry=provider_registry,
        model_registry=model_registry,
        cost_estimator=CostEstimator(model_registry),
        health_monitor=HealthMonitor(),
        max_retries=1,
        timeout_seconds=0.1,
    )

    request = GenerationRequest(
        model="gpt-4o",
        messages=[PromptMessage(role="user", content="Test")],
    )

    with pytest.raises(ProviderTimeoutException):
        await gateway.generate_text(request)


# ====================================================
# Enterprise AI Gateway V2 Mock Provider & Tests
# ====================================================
class MockV2Provider(
    ILLMProvider, IEmbeddingProvider, IImageProvider, ISpeechProvider, IVisionProvider
):
    """Unified mock provider conforming to all new contract interfaces."""

    def __init__(self, name: str, models: List[str]) -> None:
        self.name = name
        self.models = models
        self.chat_calls = 0
        self.should_fail_times = 0
        self.should_timeout = False

    def supports_model(self, model: str) -> bool:
        return model in self.models

    async def chat(self, request: ChatRequest, **kwargs: Any) -> ChatResponse:
        self.chat_calls += 1
        if self.should_fail_times > 0:
            self.should_fail_times -= 1
            raise ConnectionError("Transient network failure")
        if self.should_timeout:
            await asyncio.sleep(0.5)
        return ChatResponse(
            message=PromptMessageContract(role="assistant", content=f"Hello, {request.messages[0].content}"),
            finish_reason=FinishReason.STOP,
            model=request.model,
            provider=self.name,
        )

    async def stream_chat(
        self, request: ChatRequest, **kwargs: Any
    ) -> AsyncGenerator[StreamingChunk, None]:
        yield StreamingChunk(content="chunk")

    async def health(self):
        pass

    async def available_models(self) -> List[AIModelInfo]:
        return [
            AIModelInfo(
                name=m,
                type=ModelType.TEXT,
                context_window=2048,
                max_output_tokens=500,
                capabilities=[ProviderCapability.CHAT],
            )
            for m in self.models
        ]

    async def embed_text(self, request: EmbeddingRequest, **kwargs: Any) -> EmbeddingResponse:
        return EmbeddingResponse(embeddings=[[0.1, 0.2]], model=request.model)

    async def embed_batch(self, request: EmbeddingRequest, **kwargs: Any) -> EmbeddingResponse:
        return EmbeddingResponse(embeddings=[[0.1, 0.2]], model=request.model)

    async def generate_image(self, prompt: str, model: str, **kwargs: Any) -> str:
        return "image_url"

    async def edit_image(self, image_path: str, prompt: str, model: str, **kwargs: Any) -> str:
        return "edited_image"

    async def speech_to_text(self, audio_data: bytes, model: str, **kwargs: Any) -> str:
        return "transcript"

    async def text_to_speech(self, text: str, model: str, **kwargs: Any) -> bytes:
        return b"audio"

    async def analyze_image(self, image_path: str, prompt: str, model: str, **kwargs: Any) -> str:
        return "analysis"


@pytest.mark.anyio
async def test_aigateway_v2_registration_and_lookup() -> None:
    """Verifies that providers and models registries correctly register, list and lookup configs."""
    model_registry = ModelRegistry()
    provider_registry = ProviderRegistry()

    # Register Model Info
    model = AIModelInfo(
        name="custom-model",
        type=ModelType.TEXT,
        context_window=4096,
        max_output_tokens=1000,
        capabilities=[ProviderCapability.CHAT],
    )
    model_registry.register_model(model)
    assert model_registry.model("custom-model") == model
    assert model_registry.default_model() == "custom-model"
    assert model_registry.provider_models(ProviderCapability.CHAT) == ["custom-model"]

    # Register Provider
    provider = MockV2Provider("mock", ["custom-model"])
    provider_registry.register("mock", provider)
    assert provider_registry.provider("mock") == provider
    assert provider_registry.list() == ["mock"]
    assert provider_registry.health("mock").is_healthy is True

    # Unregister
    provider_registry.unregister("mock")
    assert provider_registry.provider("mock") is None
    assert provider_registry.list() == []


@pytest.mark.anyio
async def test_aigateway_v2_routing_completions() -> None:
    """Verifies that V2 AIGateway selects matching providers and routes requests successfully."""
    model_registry = ModelRegistry()
    provider_registry = ProviderRegistry()

    model_registry.register_model(
        AIModelInfo(
            name="gpt-4o",
            type=ModelType.TEXT,
            context_window=4096,
            max_output_tokens=1000,
            capabilities=[ProviderCapability.CHAT],
        )
    )

    provider = MockV2Provider("openai", ["gpt-4o"])
    provider_registry.register("openai", provider)

    factory = ProviderFactory(provider_registry)
    gateway = AIGateway(
        provider_registry=provider_registry,
        model_registry=model_registry,
        factory=factory,
        retry_policy=RetryPolicy(),
        timeout_policy=TimeoutPolicy(),
    )

    request = ChatRequest(
        messages=[PromptMessageContract(role="user", content="Howdy")],
        model="gpt-4o",
    )
    response = await gateway.chat(request)
    assert response.message.content == "Hello, Howdy"
    assert response.provider == "openai"


@pytest.mark.anyio
async def test_aigateway_v2_unsupported_model() -> None:
    """Verifies routing triggers ModelUnavailableError when requesting unregistered models."""
    model_registry = ModelRegistry()
    provider_registry = ProviderRegistry()
    factory = ProviderFactory(provider_registry)
    gateway = AIGateway(
        provider_registry=provider_registry,
        model_registry=model_registry,
        factory=factory,
        retry_policy=RetryPolicy(),
        timeout_policy=TimeoutPolicy(),
    )

    request = ChatRequest(
        messages=[PromptMessageContract(role="user", content="Hi")],
        model="non-existent",
    )
    with pytest.raises(ModelUnavailableError):
        await gateway.chat(request)


@pytest.mark.anyio
async def test_aigateway_v2_transient_retry_success() -> None:
    """Verifies retry policy with exponential backoff on connection errors."""
    model_registry = ModelRegistry()
    provider_registry = ProviderRegistry()

    model_registry.register_model(
        AIModelInfo(
            name="gpt-4o",
            type=ModelType.TEXT,
            context_window=4096,
            max_output_tokens=1000,
            capabilities=[ProviderCapability.CHAT],
        )
    )

    provider = MockV2Provider("openai", ["gpt-4o"])
    provider.should_fail_times = 2
    provider_registry.register("openai", provider)

    factory = ProviderFactory(provider_registry)
    gateway = AIGateway(
        provider_registry=provider_registry,
        model_registry=model_registry,
        factory=factory,
        retry_policy=RetryPolicy(max_retries=3, backoff_factor=1.1, retryable_exceptions=[ConnectionError]),
        timeout_policy=TimeoutPolicy(),
    )

    request = ChatRequest(
        messages=[PromptMessageContract(role="user", content="Hi")],
        model="gpt-4o",
    )
    response = await gateway.chat(request)
    assert response.message.content == "Hello, Hi"
    assert provider.chat_calls == 3


@pytest.mark.anyio
async def test_aigateway_v2_timeout_handling() -> None:
    """Verifies timeout policy triggers GatewayTimeoutError."""
    model_registry = ModelRegistry()
    provider_registry = ProviderRegistry()

    model_registry.register_model(
        AIModelInfo(
            name="gpt-4o",
            type=ModelType.TEXT,
            context_window=4096,
            max_output_tokens=1000,
            capabilities=[ProviderCapability.CHAT],
        )
    )

    provider = MockV2Provider("openai", ["gpt-4o"])
    provider.should_timeout = True
    provider_registry.register("openai", provider)

    factory = ProviderFactory(provider_registry)
    gateway = AIGateway(
        provider_registry=provider_registry,
        model_registry=model_registry,
        factory=factory,
        retry_policy=RetryPolicy(max_retries=1),
        timeout_policy=TimeoutPolicy(timeout_seconds=0.1),
    )

    request = ChatRequest(
        messages=[PromptMessageContract(role="user", content="Hi")],
        model="gpt-4o",
    )
    with pytest.raises(GatewayTimeoutError):
        await gateway.chat(request)


def test_gateway_configuration_model() -> None:
    """Verifies default parameters validation in GatewayConfig."""
    config = GatewayConfig()
    assert config.default_model == "gpt-4o"
    assert config.timeout_seconds == 30.0
    assert config.max_retries == 3
