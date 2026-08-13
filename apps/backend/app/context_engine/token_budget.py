"""Token Budget Engine Module.

Implements adaptive token budgeting for 4K, 8K, 16K, 32K, 64K, and 128K LLM context windows.
Automatically fits multi-tier context blocks into target token budget allocations.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.context_engine.config import ContextEngineConfig

logger = structlog.get_logger(__name__)


class TokenBudgetEngine:
    """Enterprise Adaptive Token Budgeting Engine."""

    def __init__(self, config: Optional[ContextEngineConfig] = None) -> None:
        self.config = config or ContextEngineConfig()
        logger.info("token_budget_engine_initialized")

    def estimate_tokens(self, text: str) -> int:
        """Estimates token count for text using word length heuristics (approx 1.3 tokens per word)."""
        words = text.split()
        return int(len(words) * 1.3)

    def fit_to_budget(
        self, candidates: List[Dict[str, Any]], target_budget: Optional[int] = None
    ) -> Dict[str, Any]:
        """Truncates and fits prioritized candidates into target token budget window."""
        budget = target_budget or self.config.default_token_budget
        fitted: List[Dict[str, Any]] = []
        accumulated_tokens = 0

        for item in candidates:
            content = item.get("content", "")
            tokens = self.estimate_tokens(content)

            if accumulated_tokens + tokens <= budget:
                fitted.append(item)
                accumulated_tokens += tokens
            else:
                # Partial fitting
                remaining_budget = budget - accumulated_tokens
                allowed_words = int(remaining_budget / 1.3)
                if allowed_words > 10:
                    words = content.split()[:allowed_words]
                    item_copy = dict(item)
                    item_copy["content"] = " ".join(words) + "..."
                    fitted.append(item_copy)
                    accumulated_tokens += remaining_budget
                break

        logger.info("token_budget_fit_completed", budget=budget, total_tokens=accumulated_tokens, blocks_fitted=len(fitted))
        return {
            "target_budget": budget,
            "accumulated_tokens": accumulated_tokens,
            "fitted_candidates": fitted,
            "utilization_percent": round((accumulated_tokens / max(1, budget)) * 100, 1),
        }
