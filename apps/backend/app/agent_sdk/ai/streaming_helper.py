"""StreamingHelper wrapping token stream completions.
"""

import asyncio
from typing import Any, AsyncGenerator, List, Optional, Set

from app.ai.gateway.ai_gateway import AIGateway
from app.ai.models import ChatRequest, PromptMessage, StreamingChunk
from app.agent_sdk.ai.exceptions import StreamingError


class StreamingHelper:
    """Helper wrapping language model streaming generation calls."""

    def __init__(self, gateway: AIGateway) -> None:
        """Initializes StreamingHelper.

        Args:
            gateway: Active AIGateway instance.
        """
        self.gateway = gateway
        self._active_tasks: Set[asyncio.Task[Any]] = set()

    async def stream(self, prompt: str, model: Optional[str] = None) -> AsyncGenerator[str, None]:
        """Streams text response content strings chronologically.

        Args:
            prompt: User request prompt.
            model: Optional model name.

        Yields:
            Token text string deltas.

        Raises:
            StreamingError: If stream generation fails.
        """
        target_model = model or self.gateway.model_registry.default_model() or "llama3"
        req = ChatRequest(
            model=target_model,
            messages=[PromptMessage(role="user", content=prompt)],
            stream=True,
        )
        try:
            async for chunk in self.gateway.stream_chat(req):
                yield chunk.content
        except Exception as e:
            raise StreamingError(f"Streaming failed: {str(e)}") from e

    async def stream_chunks(self, prompt: str, model: Optional[str] = None) -> AsyncGenerator[StreamingChunk, None]:
        """Streams raw StreamingChunk objects from the AI Gateway.

        Args:
            prompt: User request prompt.
            model: Optional model override.

        Yields:
            StreamingChunk object frames.

        Raises:
            StreamingError: If stream generation fails.
        """
        target_model = model or self.gateway.model_registry.default_model() or "llama3"
        req = ChatRequest(
            model=target_model,
            messages=[PromptMessage(role="user", content=prompt)],
            stream=True,
        )
        try:
            async for chunk in self.gateway.stream_chat(req):
                yield chunk
        except Exception as e:
            raise StreamingError(f"Chunk streaming failed: {str(e)}") from e

    async def stream_completion(
        self, messages: List[PromptMessage], model: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Streams response tokens for multi-turn prompt structures.

        Args:
            messages: Dialog messaging list.
            model: Optional model override.

        Yields:
            Token text string deltas.

        Raises:
            StreamingError: If stream generation fails.
        """
        target_model = model or self.gateway.model_registry.default_model() or "llama3"
        req = ChatRequest(model=target_model, messages=messages, stream=True)
        try:
            async for chunk in self.gateway.stream_chat(req):
                yield chunk.content
        except Exception as e:
            raise StreamingError(f"Completion streaming failed: {str(e)}") from e

    def cancel_stream(self, task: asyncio.Task[Any]) -> None:
        """Cancels a currently executing stream task task.

        Args:
            task: Task running a stream generator loop.
        """
        if not task.done():
            task.cancel()
