"""Streaming Manager delivering token-by-token and audio chunk streams for real-time speech responses.
"""

import asyncio
from typing import AsyncGenerator
from app.ai.conversation.interfaces import IStreamingManager


class StreamingManager(IStreamingManager):
    """Manages real-time token streaming and voice audio chunk delivery."""

    async def stream_response(self, session_id: str, prompt: str) -> AsyncGenerator[str, None]:
        """Streams token chunks asynchronously.

        Args:
            session_id: Target session ID.
            prompt: Text prompt.

        Yields:
            Token text string chunks.
        """
        words = f"Streaming response for '{prompt}'. Working on your request now.".split()
        for word in words:
            await asyncio.sleep(0.01)
            yield f"{word} "
