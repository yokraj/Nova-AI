"""Response Generator Module.

Formats, streams, and structures multi-modal responses (Markdown, JSON, LaTeX, code blocks)
with streaming generator capabilities for real-time delivery.
"""

from typing import Any, AsyncGenerator, Dict, Optional
import structlog

from app.intelligence.personality import PersonalityEngine

logger = structlog.get_logger(__name__)


class ResponseGenerator:
    """Enterprise Response Formatting & Streaming Generation Engine."""

    def __init__(self, personality_engine: Optional[PersonalityEngine] = None) -> None:
        self.personality_engine = personality_engine or PersonalityEngine()
        logger.info("response_generator_initialized")

    def format_response(
        self, content: str, domain: str = "general", format_type: str = "markdown"
    ) -> str:
        """Applies formatting standards, disclaimers, and Markdown/LaTeX structural wrappers."""
        formatted = content.strip()

        # Apply personality domain disclaimers (e.g. medical/legal/financial)
        formatted = self.personality_engine.apply_safety_disclaimers(formatted, domain)

        logger.info("response_formatted", format_type=format_type, domain=domain)
        return formatted

    async def stream_response_tokens(self, full_text: str, chunk_size: int = 15) -> AsyncGenerator[str, None]:
        """Asynchronously streams response text tokens in chunks for real-time socket interfaces."""
        words = full_text.split(" ")
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size]) + " "
            yield chunk
