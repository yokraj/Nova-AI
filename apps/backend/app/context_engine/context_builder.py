"""Context Builder Module.

Assembles final consolidated LLM context text payload from optimized context blocks.
"""

from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class ContextBuilder:
    """Enterprise Final Context Payload Assembly Engine."""

    def __init__(self) -> None:
        logger.info("context_builder_initialized")

    def build_final_context_text(
        self,
        fitted_candidates: List[Dict[str, Any]],
        user_preferences: Optional[Dict[str, Any]] = None,
        workspace: str = "Nova",
        project: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Formats optimized candidates into a structured context text block."""
        blocks: List[str] = []

        if user_preferences:
            blocks.append(f"--- USER PREFERENCES ---\nStyle: {user_preferences.get('writing_style', 'Concise')}")

        blocks.append(f"--- ENVIRONMENT ---\nWorkspace: {workspace} | Project: {project or 'General'}")

        items_text = []
        for idx, item in enumerate(fitted_candidates, 1):
            source = item.get("source", "knowledge").upper()
            title = item.get("title", f"Block #{idx}")
            content = item.get("content", "")
            items_text.append(f"[{idx}] ({source}) {title}:\n{content}")

        if items_text:
            blocks.append("--- CONTEXT KNOWLEDGE BLOCKS ---\n" + "\n\n".join(items_text))
        else:
            blocks.append("--- CONTEXT KNOWLEDGE BLOCKS ---\n[No context blocks available.]")

        final_text = "\n\n".join(blocks)
        logger.info("final_context_text_assembled", total_len=len(final_text), blocks_count=len(fitted_candidates))

        return {
            "context_text": final_text,
            "blocks_count": len(fitted_candidates),
            "sources": [c.get("source") for c in fitted_candidates],
        }
