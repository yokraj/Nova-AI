"""Query Rewriter Module.

Rewrites ambiguous questions, resolves pronouns, expands follow-up references,
and contextualizes incomplete requests for precision retrieval.
"""

from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class QueryRewriter:
    """Enterprise RAG Contextual Query Expansion & Rewriting Engine."""

    def __init__(self) -> None:
        logger.info("query_rewriter_initialized")

    def rewrite_query(
        self,
        raw_query: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        active_project: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Rewrites and expands raw user query with context resolution."""
        rewritten = raw_query.strip()
        expanded_terms: List[str] = []

        # 1. Pronoun / Follow-Up Resolution
        if any(p in raw_query.lower() for p in ["it", "this", "that", "them", "the previous"]):
            if conversation_history:
                last_turn = conversation_history[-1].get("content", "")
                if last_turn:
                    extracted_context = last_turn[:60]
                    rewritten += f" (Context: {extracted_context})"
                    expanded_terms.append(extracted_context)

        # 2. Active Project Contextualization
        if active_project and active_project.lower() not in rewritten.lower():
            rewritten += f" regarding {active_project}"
            expanded_terms.append(active_project)

        logger.info("query_rewritten", original=raw_query, rewritten=rewritten)
        return {
            "original_query": raw_query,
            "rewritten_query": rewritten,
            "expanded_terms": expanded_terms,
            "is_modified": raw_query != rewritten,
        }
