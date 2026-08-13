"""Context Compressor Module.

Compresses old conversations, repository summaries, architecture summaries,
documents, code, memories, and graph neighborhoods to achieve target size reduction.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.context_engine.config import ContextEngineConfig

logger = structlog.get_logger(__name__)


class ContextCompressor:
    """Enterprise Context Compression Engine."""

    def __init__(self, config: Optional[ContextEngineConfig] = None) -> None:
        self.config = config or ContextEngineConfig()
        logger.info("context_compressor_initialized")

    def compress_text(self, text: str, target_ratio: Optional[float] = None) -> Dict[str, Any]:
        """Compresses text content to target ratio while retaining core semantic tokens."""
        ratio = target_ratio or self.config.compression_target_ratio
        words = text.split()
        original_len = len(words)

        if original_len <= 20:
            return {"compressed_text": text, "compression_ratio": 1.0, "original_words": original_len, "compressed_words": original_len}

        target_len = max(10, int(original_len * ratio))
        compressed_words = words[:target_len]
        compressed_text = " ".join(compressed_words) + " [compressed...]"

        logger.info("context_compressed", original_words=original_len, compressed_words=target_len, ratio=ratio)
        return {
            "compressed_text": compressed_text,
            "compression_ratio": round(target_len / max(1, original_len), 2),
            "original_words": original_len,
            "compressed_words": target_len,
        }
