"""Unit tests for the Agent SDK AI Helper Library.

Verifies chat, streaming, embedding, vision, completion, model, and token helpers.
"""

import asyncio
from typing import Any, AsyncGenerator, Dict, List
import pytest

from app.agent_sdk.ai import (
    ChatHelper,
    StreamingHelper,
    EmbeddingHelper,
    VisionHelper,
    CompletionHelper,
    ModelHelper,
    TokenHelper,
    AIHelperError,
    EmbeddingError,
    VisionError,
)
from app.ai.gateway.ai_gateway import AIGateway
from app.ai.gateway.model_registry import ModelRegistry
from app.ai.gateway.provider_registry import ProviderRegistry
from app.ai.models import (
    ChatResponse,
    PromptMessage,
    FinishReason,
    StreamingChunk,
    AIModelInfo,
    ModelType,
    ProviderCapability,
)


class DummyProvider:
    """Mock provider supporting model capability checks."""

    def supports_model(self, model_name: str) -> bool:
        return True


class MockGateway(AIGateway):
    """Stubbed AIGateway for local zero-cost helper library testing."""

    def __init__(self) -> None:
        self.model_registry = ModelRegistry()
        self.provider_registry = ProviderRegistry()

        self.model_registry.register_model(
            AIModelInfo(
                name="llama3",
                type=ModelType.TEXT,
                context_window=8192,
                max_output_tokens=2048,
                capabilities=[ProviderCapability.CHAT, ProviderCapability.VISION],
            ),
            is_default=True,
        )
        self.provider_registry.register("mock", DummyProvider())

    async def chat(self, request: Any, **kwargs: Any) -> ChatResponse:
        content = "Mock response content"
        for msg in request.messages:
            if "json" in msg.content.lower():
                content = '{"status": "success", "result": "parsed"}'
                break
            elif "summarize" in msg.content.lower():
                content = "Summary result"
                break
            elif "rewrite" in msg.content.lower():
                content = "Rewritten result"
                break
            elif "explain" in msg.content.lower():
                content = "Explained topic"
                break
            elif "translate" in msg.content.lower():
                content = "Bonjour"
                break

        return ChatResponse(
            message=PromptMessage(role="assistant", content=content),
            finish_reason=FinishReason.STOP,
            model="llama3",
            provider="mock",
        )

    async def stream_chat(
        self, request: Any, **kwargs: Any
    ) -> AsyncGenerator[StreamingChunk, None]:
        yield StreamingChunk(content="Mock ")
        yield StreamingChunk(content="stream ")
        yield StreamingChunk(content="output")


@pytest.fixture
def gateway_setup() -> MockGateway:
    """Fixture to build active mock gateway."""
    return MockGateway()


@pytest.mark.anyio
async def test_chat_helper(gateway_setup: MockGateway) -> None:
    """Verifies ChatHelper execution methods."""
    helper = ChatHelper(gateway_setup)

    # General chat
    res = await helper.chat("hello")
    assert res == "Mock response content"

    # System prompt chat
    res_sys = await helper.chat_with_system_prompt("hello", "sys instructions")
    assert res_sys == "Mock response content"

    # Multi-turn
    res_multi = await helper.multi_turn_chat([{"role": "user", "content": "hi"}])
    assert res_multi == "Mock response content"

    # Structured chat JSON parsing
    res_struct = await helper.structured_chat("parse this json", schema={"type": "object"})
    assert isinstance(res_struct, dict)
    assert res_struct["status"] == "success"

    # Conversation chat
    res_conv = await helper.conversation_chat("hello", conversation_id=uuid_or_dummy())
    assert res_conv == "Mock response content"


@pytest.mark.anyio
async def test_completion_helper(gateway_setup: MockGateway) -> None:
    """Verifies CompletionHelper prompts delegation."""
    helper = CompletionHelper(gateway_setup)

    assert await helper.complete("complete me") == "Mock response content"
    assert await helper.summarize("long text") == "Summary result"
    assert await helper.rewrite("old text") == "Rewritten result"
    assert await helper.explain("deep topic") == "Explained topic"
    assert await helper.translate("hello") == "Bonjour"


def test_model_helper(gateway_setup: MockGateway) -> None:
    """Verifies ModelHelper registration details query mapping."""
    helper = ModelHelper(gateway_setup)

    assert "llama3" in helper.list_models()
    assert helper.current_model() == "llama3"
    assert helper.current_provider() == "mock"
    assert "chat" in helper.model_capabilities("llama3")


def test_token_helper(gateway_setup: MockGateway) -> None:
    """Verifies TokenHelper character estimations and truncations."""
    helper = TokenHelper(gateway_setup)

    # Estimate (1 token per 4 characters)
    assert helper.estimate("12345678") == 2
    assert helper.estimate("") == 0

    # Remaining context (8192 - 2)
    assert helper.remaining_context("12345678", "llama3") == 8190

    # Truncate
    text = "1234567890"
    # max_tokens = 1 => budget = 4 chars
    assert helper.truncate(text, 1) == "1234"


@pytest.mark.anyio
async def test_streaming_helper(gateway_setup: MockGateway) -> None:
    """Verifies StreamingHelper generators yield content segments."""
    helper = StreamingHelper(gateway_setup)

    # Stream text contents
    stream_tokens = []
    async for chunk in helper.stream("prompt"):
        stream_tokens.append(chunk)
    assert "".join(stream_tokens) == "Mock stream output"

    # Stream raw chunks
    stream_chunks = []
    async for chunk in helper.stream_chunks("prompt"):
        stream_chunks.append(chunk)
    assert len(stream_chunks) == 3
    assert stream_chunks[0].content == "Mock "

    # Stream completions
    msgs_tokens = []
    async for chunk in helper.stream_completion([PromptMessage(role="user", content="msg")]):
        msgs_tokens.append(chunk)
    assert "".join(msgs_tokens) == "Mock stream output"


@pytest.mark.anyio
async def test_embedding_helper_placeholders(gateway_setup: MockGateway) -> None:
    """Verifies EmbeddingHelper placeholders and math vector computations."""
    helper = EmbeddingHelper(gateway_setup)

    # Placeholder embeds
    vec = await helper.embed("hello")
    assert len(vec) == 5
    assert vec == [0.1, 0.2, 0.3, 0.4, 0.5]

    docs = await helper.embed_documents(["doc1", "doc2"])
    assert len(docs) == 2
    assert docs[0] == vec

    # Empty check raises
    with pytest.raises(EmbeddingError):
        await helper.embed("")

    # Similarity
    sim = await helper.similarity("text1", "text2")
    assert sim == 1.0  # since both return the exact same mock vector

    # Cosine Similarity math checks
    assert helper.cosine_similarity([1.0, 0.0], [0.0, 1.0]) == 0.0
    assert helper.cosine_similarity([1.0, 0.0], [1.0, 0.0]) == 1.0


@pytest.mark.anyio
async def test_vision_helper_placeholders(gateway_setup: MockGateway) -> None:
    """Verifies VisionHelper placeholders checking validation limits."""
    helper = VisionHelper(gateway_setup)

    # describe_image
    desc = await helper.describe_image(b"image_bytes")
    assert "Described image content" in desc

    # analyze_ui
    ui_elements = await helper.analyze_ui(b"screenshot")
    assert "elements" in ui_elements

    # ocr
    ocr_text = await helper.ocr(b"ocr")
    assert "Extracted OCR text" in ocr_text

    # detect_objects
    objects = await helper.detect_objects(b"objects")
    assert len(objects) == 1
    assert objects[0]["class"] == "person"

    # Validation errors checks
    with pytest.raises(VisionError):
        await helper.describe_image(b"")


def uuid_or_dummy() -> Any:
    """Helper to return a dummy UUID."""
    return uuid4_mock()


def uuid4_mock() -> Any:
    """Return a standard UUID."""
    import uuid

    return uuid.uuid4()
