"""Unit tests for the Ollama Provider.

Verifies chat completions, text stream generation, embeddings, health checking,
and registry configuration checks.
"""

from typing import Any, AsyncGenerator, Dict
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from pydantic import ValidationError

from app.ai.providers.ollama import (
    OllamaClient,
    OllamaConfig,
    OllamaHealthCheck,
    OllamaProvider,
    OllamaProviderError,
)
from app.ai.models import (
    ChatRequest,
    EmbeddingRequest,
    PromptMessage,
    ProviderCapability,
)
from app.ai.gateway import ProviderRegistry


@pytest.fixture
def ollama_config() -> OllamaConfig:
    """Fixture returning baseline Ollama config."""
    return OllamaConfig(host="http://localhost:11434", timeout_seconds=5.0, default_model="llama3")


@pytest.fixture
def mock_client(ollama_config) -> MagicMock:
    """Fixture returning mock OllamaClient."""
    client = MagicMock(spec=OllamaClient)
    client.config = ollama_config
    return client


@pytest.fixture
def provider(ollama_config, mock_client) -> OllamaProvider:
    """Fixture returning OllamaProvider instance."""
    return OllamaProvider(ollama_config, mock_client)


@pytest.mark.anyio
async def test_ollama_chat_success(provider, mock_client) -> None:
    """Verifies chat completion parses response usage tokens."""
    mock_client.post.return_value = {
        "message": {"role": "assistant", "content": "Hello user"},
        "prompt_eval_count": 10,
        "eval_count": 20,
    }

    request = ChatRequest(
        messages=[PromptMessage(role="user", content="Hi")],
        model="llama3",
    )

    response = await provider.chat(request)
    assert response.message.content == "Hello user"
    assert response.message.role == "assistant"
    assert response.usage.token_usage.prompt_tokens == 10
    assert response.usage.token_usage.completion_tokens == 20
    assert response.usage.token_usage.total_tokens == 30
    assert response.provider == "ollama"


@pytest.mark.anyio
async def test_ollama_stream_chat_success(provider, mock_client) -> None:
    """Verifies stream_chat yields incremental token deltas."""
    async def mock_stream(*args, **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        yield {"message": {"content": "Hello "}, "done": False}
        yield {"message": {"content": "world"}, "done": True, "prompt_eval_count": 5, "eval_count": 10}

    mock_client.post_stream = mock_stream

    request = ChatRequest(
        messages=[PromptMessage(role="user", content="Hi")],
        model="llama3",
        stream=True,
    )

    chunks = []
    async for chunk in provider.stream_chat(request):
        chunks.append(chunk)

    assert len(chunks) == 2
    assert chunks[0].content == "Hello "
    assert chunks[0].finish_reason is None
    assert chunks[1].content == "world"
    assert chunks[1].finish_reason == "stop"
    assert chunks[1].usage.token_usage.total_tokens == 15


@pytest.mark.anyio
async def test_ollama_embeddings_success(provider, mock_client) -> None:
    """Verifies embeddings retrieves vector arrays."""
    mock_client.post.return_value = {
        "embedding": [0.1, 0.2, 0.3],
    }

    request = EmbeddingRequest(
        input=["hello"],
        model="nomic-embed-text",
    )

    response = await provider.embed_text(request)
    assert len(response.embeddings) == 1
    assert response.embeddings[0] == [0.1, 0.2, 0.3]


@pytest.mark.anyio
async def test_ollama_health_check_success(provider, mock_client) -> None:
    """Verifies health check is true if server is reachable and model is pulled."""
    mock_client.get.return_value = {
        "models": [{"name": "llama3:latest"}, {"name": "nomic-embed-text:latest"}]
    }

    health = await provider.health()
    assert health.is_healthy is True
    assert health.status_code == 200


@pytest.mark.anyio
async def test_ollama_health_check_model_missing(provider, mock_client) -> None:
    """Verifies health check is false if requested model is not found."""
    mock_client.get.return_value = {
        "models": [{"name": "mistral:latest"}]
    }

    health = await provider.health()
    assert health.is_healthy is False
    assert health.status_code == 404


@pytest.mark.anyio
async def test_ollama_health_check_server_offline(provider, mock_client) -> None:
    """Verifies health check is false if server query fails."""
    mock_client.get.side_effect = Exception("Connection refused")

    health = await provider.health()
    assert health.is_healthy is False
    assert health.status_code == 503


def test_ollama_provider_registration() -> None:
    """Verifies registration and capability checks within ProviderRegistry."""
    registry = ProviderRegistry()
    config = OllamaConfig()
    client = OllamaClient(config)
    provider = OllamaProvider(config, client)

    registry.register("ollama", provider)
    assert registry.provider("ollama") == provider
    assert registry.list() == ["ollama"]
    assert registry.capabilities("ollama") == [ProviderCapability.CHAT, ProviderCapability.EMBEDDINGS]
