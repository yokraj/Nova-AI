"""Context Builder Module.

Constructs consolidated multi-domain LLM context incorporating Memory, Conversations,
Documents, Code snippets, Project history, User preferences, Workspace settings, and Architectural decisions.
"""

from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class ContextBuilder:
    """Enterprise Consolidated LLM Context Assembly Engine."""

    def __init__(self) -> None:
        logger.info("context_builder_initialized")

    def build_context_package(
        self,
        retrieved_chunks: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        user_preferences: Optional[Dict[str, Any]] = None,
        workspace: str = "Nova",
        project: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Assembles structured context payload combining retrieved chunks and environmental metadata."""
        context_blocks: List[str] = []

        # 1. User Preferences Block
        if user_preferences:
            pref_line = f"User Profile: Writing Style: {user_preferences.get('writing_style')}. Languages: {user_preferences.get('favorite_languages')}."
            context_blocks.append(f"--- USER PREFERENCES ---\n{pref_line}")

        # 2. Workspace & Project Context Block
        env_line = f"Active Workspace: {workspace} | Active Project: {project or 'General'}"
        context_blocks.append(f"--- ENVIRONMENT ---\n{env_line}")

        # 3. Retrieved Knowledge & Memory Chunks
        chunk_lines = []
        for idx, chunk in enumerate(retrieved_chunks, 1):
            title = chunk.get("title", f"Source Item #{idx}")
            mem_id = chunk.get("memory_id", f"source-{idx}")
            content = chunk.get("content", "")
            chunk_lines.append(f"[{idx}] Source ID ({mem_id}) - {title}:\n{content}")

        if chunk_lines:
            context_blocks.append("--- RETRIEVED KNOWLEDGE & MEMORIES ---\n" + "\n\n".join(chunk_lines))
        else:
            context_blocks.append("--- RETRIEVED KNOWLEDGE & MEMORIES ---\n[No specific grounding documents retrieved.]")

        # 4. Recent Conversation History Block
        if conversation_history:
            history_lines = [f"{msg.get('role', 'user').capitalize()}: {msg.get('content', '')}" for msg in conversation_history[-5:]]
            context_blocks.append("--- CONVERSATION HISTORY ---\n" + "\n".join(history_lines))

        full_context_text = "\n\n".join(context_blocks)
        logger.info("context_package_built", block_count=len(context_blocks), char_len=len(full_context_text))

        return {
            "context_text": full_context_text,
            "chunk_count": len(retrieved_chunks),
            "sources": [{"memory_id": c.get("memory_id"), "title": c.get("title")} for c in retrieved_chunks],
        }
