"""Cost tracking and token metric estimators for Nova AI Gateway.

Computes query pricing metrics per model rate and tracks provider statistics.
"""

from typing import Dict
import structlog

from app.ai.registry import ModelRegistry

logger = structlog.get_logger(__name__)


class ProviderStats:
    """Statistics accumulator tracking metrics for a provider."""

    def __init__(self) -> None:
        self.request_count: int = 0
        self.prompt_tokens: int = 0
        self.completion_tokens: int = 0
        self.total_tokens: int = 0
        self.estimated_cost: float = 0.0


class CostEstimator:
    """Helper calculating and storing monetary tokens metrics."""

    def __init__(self, model_registry: ModelRegistry) -> None:
        """Initializes the CostEstimator.

        Args:
            model_registry: The ModelRegistry database of model rates.
        """
        self.model_registry = model_registry
        self.stats: Dict[str, ProviderStats] = {}

    def calculate_cost(
        self, model: str, prompt_tokens: int, completion_tokens: int
    ) -> float:
        """Calculates the estimated query cost in USD.

        Args:
            model: The name of the target model.
            prompt_tokens: Number of prompt/input tokens.
            completion_tokens: Number of output/completion tokens.

        Returns:
            The estimated cost in USD rounded to 6 decimal places.
        """
        metadata = self.model_registry.get(model)
        if not metadata:
            return 0.0
        input_cost = (prompt_tokens / 1000.0) * metadata.input_cost_per_1k
        output_cost = (completion_tokens / 1000.0) * metadata.output_cost_per_1k
        return round(input_cost + output_cost, 6)

    def track_metrics(
        self,
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> float:
        """Tracks query call statistics and returns the cost value.

        Args:
            provider: Name of the active provider.
            model: Model identifier name.
            prompt_tokens: Input tokens count.
            completion_tokens: Generated tokens count.

        Returns:
            The calculated cost value.
        """
        cost = self.calculate_cost(model, prompt_tokens, completion_tokens)

        if provider not in self.stats:
            self.stats[provider] = ProviderStats()

        stats = self.stats[provider]
        stats.request_count += 1
        stats.prompt_tokens += prompt_tokens
        stats.completion_tokens += completion_tokens
        stats.total_tokens += prompt_tokens + completion_tokens
        stats.estimated_cost += cost

        logger.info(
            "ai_cost_tracked",
            provider=provider,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost=cost,
        )
        return cost
