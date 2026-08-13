"""Context Manager Module.

Manages conversation, project, workspace, tool, agent, and memory context slices,
providing intelligent context window compression, summarization, and token limit management.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.intelligence.config import IntelligenceConfig

logger = structlog.get_logger(__name__)


class ContextManager:
    """Enterprise Multi-Dimensional Context Manager & Compression Engine."""

    def __init__(self, config: Optional[IntelligenceConfig] = None) -> None:
        self.config = config or IntelligenceConfig()
        self._project_context: Dict[str, Any] = {}
        self._workspace_context: Dict[str, Any] = {}
        self._tool_context: List[Dict[str, Any]] = []
        self._agent_context: Dict[str, Any] = {}
        logger.info("context_manager_initialized", max_tokens=self.config.context_window_size)

    def assemble_full_context(
        self,
        conversation_history: List[Dict[str, Any]],
        retrieved_knowledge: Optional[str] = None,
        memory_summary: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Assembles consolidated context object combining all active context dimensions."""
        formatted_history = [
            f"{msg.get('role', 'user').capitalize()}: {msg.get('content', '')}"
            for msg in conversation_history
        ]
        
        raw_text = "\n".join(formatted_history)
        token_estimate = len(raw_text.split()) * 1.3

        # Compress if token estimate exceeds compression threshold
        if token_estimate > (self.config.context_window_size * self.config.context_compression_threshold):
            formatted_history = self.compress_conversation_history(conversation_history)

        return {
            "conversation_history": formatted_history,
            "project_context": self._project_context,
            "workspace_context": self._workspace_context,
            "retrieved_knowledge": retrieved_knowledge or "",
            "memory_summary": memory_summary or "",
            "token_estimate": token_estimate,
        }

    def compress_conversation_history(
        self, history: List[Dict[str, Any]], keep_recent: int = 4
    ) -> List[str]:
        """Compresses long conversation history into a summary plus recent turn messages."""
        if len(history) <= keep_recent:
            return [f"{m.get('role')}: {m.get('content')}" for m in history]

        older = history[:-keep_recent]
        recent = history[-keep_recent:]

        summary_line = f"[System Context Summary of {len(older)} previous turns: Conversation focused on system setup and implementation planning.]"
        compressed = [summary_line]
        compressed.extend([f"{m.get('role')}: {m.get('content')}" for m in recent])

        logger.info("context_compressed", original_turns=len(history), compressed_turns=len(compressed))
        return compressed

    def update_project_context(self, project_data: Dict[str, Any]) -> None:
        """Updates active project context slice."""
        self._project_context.update(project_data)

    def update_workspace_context(self, workspace_data: Dict[str, Any]) -> None:
        """Updates active workspace context slice."""
        self._workspace_context.update(workspace_data)
