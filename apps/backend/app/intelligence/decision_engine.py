"""Decision Engine Module.

Implements DecisionEngine determining resource requirements (memory, tools, RAG, coding, browser,
internet search, multi-agent workforce, clarification requests) for incoming requests.
"""

from typing import Any, Dict, Optional
import structlog

logger = structlog.get_logger(__name__)


class DecisionEngine:
    """Enterprise Autonomous Capabilities & Resource Routing Decision Engine."""

    def __init__(self) -> None:
        logger.info("decision_engine_initialized")

    def evaluate_request(self, user_input: str, conversation_length: int = 0) -> Dict[str, Any]:
        """Evaluates input to determine resource and module needs."""
        input_lower = user_input.lower()

        need_memory = conversation_length > 0 or any(t in input_lower for t in ["remember", "previous", "earlier", "my name", "my project"])
        need_tools = any(t in input_lower for t in ["run", "calculate", "search", "terminal", "file", "git", "sql", "database", "python"])
        need_rag = any(t in input_lower for t in ["document", "pdf", "repo", "architecture", "spec", "knowledge", "system"])
        need_coding = any(t in input_lower for t in ["code", "function", "script", "python", "typescript", "bug", "refactor"])
        need_browser = any(t in input_lower for t in ["website", "url", "scrape", "browse"])
        need_internet = any(t in input_lower for t in ["latest", "news", "today", "weather", "search web"])
        need_multiple_agents = any(t in input_lower for t in ["build", "system", "full app", "complete workflow", "end to end", "management system"])
        need_clarification = len(user_input.split()) < 2 and not any(t in input_lower for t in ["hi", "hello", "help", "yes", "no"])

        decisions = {
            "need_memory": need_memory,
            "need_tools": need_tools,
            "need_rag": need_rag,
            "need_coding": need_coding,
            "need_browser": need_browser,
            "need_internet": need_internet,
            "need_multiple_agents": need_multiple_agents,
            "need_clarification": need_clarification,
        }

        logger.info("decisions_evaluated", decisions=decisions)
        return decisions
