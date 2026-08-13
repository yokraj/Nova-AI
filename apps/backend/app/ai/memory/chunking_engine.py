"""Chunking Engine splits text documents into tokens-bounded chunks.
"""

from typing import List, Dict, Any
from app.ai.memory.models import DocumentChunk

class DocumentChunker:
    """Chunks text contents adhering to size boundaries and overlaps."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, parsed_doc: Dict[str, Any]) -> List[DocumentChunk]:
        """Slices parsed content text into overlapping chunks."""
        content = parsed_doc["content"]
        source = parsed_doc["source"]
        metadata = parsed_doc["metadata"]

        chunks = []
        if not content:
            return chunks

        # Basic character/token approximation slicing
        # In a production engine, this would use a real tokenizer,
        # but a character-based window serves as a clean, local-first strategy.
        start = 0
        chunk_idx = 0
        content_len = len(content)

        while start < content_len:
            end = start + self.chunk_size
            chunk_content = content[start:end]
            
            # Simple token count estimation (approx 4 chars per token)
            estimated_tokens = len(chunk_content) // 4

            chunk_meta = metadata.copy()
            chunk_meta["chunk_index"] = chunk_idx

            chunks.append(
                DocumentChunk(
                    document_id=source,
                    chunk_index=chunk_idx,
                    content=chunk_content,
                    tokens=max(1, estimated_tokens),
                    metadata=chunk_meta
                )
            )

            # Move window forward, accounting for overlap
            start += (self.chunk_size - self.chunk_overlap)
            chunk_idx += 1

            # Infinite loop safety guard
            if self.chunk_size <= self.chunk_overlap:
                break

        return chunks
