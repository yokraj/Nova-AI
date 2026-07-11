"""Unit tests for the new AI Platform Contracts.

Verifies abstract base class inheritance interfaces, enums values, and Pydantic validation.
"""

from typing import AsyncGenerator
import pytest
from pydantic import ValidationError

from app.ai.models import (
    AIModelInfo,
    ChatRequest,
    ChatResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    FinishReason,
    MessageRole,
    ModelType,
    PromptMessage,
    ProviderCapability,
    ProviderMetadata,
    ProviderType,
    StreamingChunk,
)
from app.ai.providers.contracts import (
    IEmbeddingProvider,
    IImageProvider,
    ILLMProvider,
    ISpeechProvider,
    IVisionProvider,
)
from app.ai.gateway import (
    IAIGateway,
    IProviderFactory,
)
from app.ai.shared import (
    AIException,
    CapabilityResolver,
    CapabilityUnavailable,
    GatewayException,
    ModelSelector,
    ModelUnavailable,
    ProviderNotFound,
    ProviderUnavailable,
    providerValidator,
)


class DummyLLM(ILLMProvider):
    """Minimal dummy implementation to verify ILLMProvider inheritance."""

    async def chat(self, request: ChatRequest, **kwargs) -> ChatResponse:
        return ChatResponse(
            message=PromptMessage(role="assistant", content="Hi"),
            finish_reason=FinishReason.STOP,
            model="gpt-4o",
            provider="dummy",
        )

    async def stream_chat(
        self, request: ChatRequest, **kwargs
    ) -> AsyncGenerator[StreamingChunk, None]:
        yield StreamingChunk(content="chunk")

    async def health(self):
        pass

    async def available_models(self):
        pass


def test_interface_inheritance() -> None:
    """Verifies subclass inheritance behaves correctly with abstract contracts."""
    dummy = DummyLLM()
    assert isinstance(dummy, ILLMProvider)
    assert not isinstance(dummy, IEmbeddingProvider)
    assert not isinstance(dummy, IImageProvider)
    assert not isinstance(dummy, ISpeechProvider)
    assert not isinstance(dummy, IVisionProvider)


def test_provider_validator_utility() -> None:
    """Verifies that providerValidator correctly identifies supported capabilities."""
    dummy = DummyLLM()
    assert providerValidator.validate(dummy, ProviderCapability.CHAT) is True
    assert providerValidator.validate(dummy, ProviderCapability.EMBEDDINGS) is False


def test_enums_integrity() -> None:
    """Verifies enum types and string values mappings."""
    assert ProviderType.OPENAI == "openai"
    assert ProviderCapability.CHAT == "chat"
    assert ModelType.TEXT == "text"
    assert MessageRole.ASSISTANT == "assistant"
    assert FinishReason.STOP == "stop"


def test_chat_request_pydantic_validation() -> None:
    """Verifies Pydantic validation handles correct and incorrect ChatRequest inputs."""
    # Correct request
    req = ChatRequest(
        messages=[PromptMessage(role="user", content="Hello")],
        model="gpt-4o",
    )
    assert req.model == "gpt-4o"
    assert len(req.messages) == 1

    # Missing model field
    with pytest.raises(ValidationError):
        ChatRequest(messages=[PromptMessage(role="user", content="Hello")])  # type: ignore


def test_chat_response_validation() -> None:
    """Verifies ChatResponse schema validation works."""
    res = ChatResponse(
        message=PromptMessage(role="assistant", content="Test output"),
        finish_reason=FinishReason.STOP,
        model="gpt-4o",
        provider="openai",
    )
    assert res.message.content == "Test output"
    assert res.provider == "openai"


def test_capability_resolver_utility() -> None:
    """Verifies capability resolver matches method string keys correctly."""
    assert CapabilityResolver.map_action_to_capability("chat") == ProviderCapability.CHAT
    assert CapabilityResolver.map_action_to_capability("embed_text") == ProviderCapability.EMBEDDINGS
    assert CapabilityResolver.map_action_to_capability("invalid_action") is None


def test_model_selector_utility() -> None:
    """Verifies model selector filters lists matching capability parameters."""
    models_list = [
        AIModelInfo(
            name="text-model",
            type=ModelType.TEXT,
            context_window=1000,
            max_output_tokens=100,
            capabilities=[ProviderCapability.CHAT],
        ),
        AIModelInfo(
            name="vision-model",
            type=ModelType.MULTIMODAL,
            context_window=2000,
            max_output_tokens=200,
            capabilities=[ProviderCapability.VISION],
        ),
    ]

    selected = ModelSelector.select_model(models_list, ProviderCapability.VISION)
    assert selected == "vision-model"

    none_selected = ModelSelector.select_model(models_list, ProviderCapability.IMAGE)
    assert none_selected is None


def test_custom_exceptions() -> None:
    """Verifies custom exceptions properties and structures."""
    with pytest.raises(AIException):
        raise ProviderUnavailable("Provider offline")

    with pytest.raises(AIException):
        raise ProviderNotFound("Provider missing")

    with pytest.raises(AIException):
        raise ModelUnavailable("Model inactive")

    with pytest.raises(AIException):
        raise CapabilityUnavailable("Capability unsupported")

    with pytest.raises(AIException):
        raise GatewayException("Gateway failed")
