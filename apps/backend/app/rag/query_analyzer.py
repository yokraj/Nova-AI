"""Query Analyzer Module.

Classifies incoming user queries into domain intent categories (Question, Conversation, Coding,
Research, Project lookup, Memory lookup, Document lookup, Summarization, Comparison, Planning).
"""

from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class QueryAnalyzer:
    """Enterprise RAG Query Intent Classification Engine."""

    def __init__(self) -> None:
        self.categories: List[str] = [
            "question",
            "conversation",
            "coding",
            "research",
            "project_lookup",
            "memory_lookup",
            "document_lookup",
            "summarization",
            "comparison",
            "planning",
        ]
        logger.info("query_analyzer_initialized")

    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyzes query string to extract intent category, entities, and keyword tokens."""
        q_lower = query.lower()

        if any(t in q_lower for t in ["code", "function", "script", "def ", "class ", "bug", "refactor"]):
            intent = "coding"
        elif any(t in q_lower for t in ["compare", "versus", "difference between"]):
            intent = "comparison"
        elif any(t in q_lower for t in ["summarize", "summary", "overview"]):
            intent = "summarization"
        elif any(t in q_lower for t in ["project", "architecture", "decision"]):
            intent = "project_lookup"
        elif any(t in q_lower for t in ["remember", "previous", "memory", "my preference"]):
            intent = "memory_lookup"
        elif any(t in q_lower for t in ["doc", "pdf", "file", "specification"]):
            intent = "document_lookup"
        elif any(t in q_lower for t in ["plan", "build", "system", "steps to", "management system"]):
            intent = "planning"
        elif any(t in q_lower for t in ["paper", "literature", "search"]):
            intent = "research"
        elif any(t in q_lower for t in ["what", "how", "why", "who", "when"]):
            intent = "question"
        else:
            intent = "conversation"

        logger.info("query_analyzed", query_snippet=query[:30], intent=intent)
        return {
            "query": query,
            "intent_category": intent,
            "tokens": [t for t in query.split() if len(t) > 2],
            "requires_retrieval": intent not in ["conversation"],
        }
