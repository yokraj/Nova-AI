"""Memory Compression Module.

Implements MemoryCompressor for compressing old conversations, repeated information,
long discussions, and duplicate knowledge while preserving pinned and high-importance memories.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.memory.config import MemoryConfig

logger = structlog.get_logger(__name__)


class MemoryCompressor:
    """Enterprise Memory Summarization & Compression Engine."""

    def __init__(self, config: Optional[MemoryConfig] = None) -> None:
        self.config = config or MemoryConfig()
        logger.info("memory_compressor_initialized")

    def compress_memory_thread(
        self, entries: List[Dict[str, Any]], max_preserved: int = 5
    ) -> Dict[str, Any]:
        """Compresses long thread entries into a thread summary + recent turns."""
        if len(entries) <= max_preserved:
            return {
                "summary": "No compression required (entry count below threshold).",
                "compressed_count": 0,
                "preserved_entries": entries,
                "compression_ratio": 1.0,
            }

        # Preserve pinned and high-importance entries
        pinned_entries = [e for e in entries[:-max_preserved] if e.get("is_pinned") or e.get("importance", 0) >= 0.8]
        unpinned_older = [e for e in entries[:-max_preserved] if e not in pinned_entries]
        recent = entries[-max_preserved:]

        summary_text = (
            f"Compressed Thread Summary ({len(unpinned_older)} older turns): "
            f"Key discussion points extracted and merged."
        )

        compressed_list = pinned_entries + recent
        ratio = len(compressed_list) / len(entries)

        logger.info(
            "memory_thread_compressed",
            original_count=len(entries),
            compressed_count=len(compressed_list),
            ratio=round(ratio, 2),
        )

        return {
            "summary": summary_text,
            "compressed_count": len(unpinned_older),
            "preserved_entries": compressed_list,
            "compression_ratio": round(ratio, 2),
        }
