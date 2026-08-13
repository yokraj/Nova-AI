"""Cost Estimator Module.

Estimates cloud API costs, GPU operational costs, energy consumption (kWh), and inference times.
"""

from typing import Any, Dict
import structlog

logger = structlog.get_logger(__name__)


class CostEstimator:
    """Enterprise Inference Cost & Energy Estimator."""

    def estimate_cost(
        self, provider: str, prompt_tokens: int, completion_tokens: int, gpu_hours: float = 0.001
    ) -> Dict[str, Any]:
        """Estimates cost and energy usage for local vs cloud inference."""
        if provider.lower() in ["openai", "anthropic", "gemini"]:
            # Cloud pricing estimate ($2.50 / 1M prompt, $10.00 / 1M completion)
            cloud_cost = (prompt_tokens * 0.0000025) + (completion_tokens * 0.000010)
            gpu_energy_kwh = 0.0
        else:
            # Local GPU energy cost (~350W GPU * hours)
            cloud_cost = 0.0
            gpu_energy_kwh = round(0.350 * gpu_hours, 4)

        logger.info("cost_estimated", provider=provider, cloud_cost=cloud_cost, kwh=gpu_energy_kwh)
        return {
            "provider": provider,
            "estimated_cloud_cost_usd": round(cloud_cost, 6),
            "estimated_energy_kwh": gpu_energy_kwh,
            "local_gpu_cost_usd": round(gpu_energy_kwh * 0.15, 6),  # $0.15 / kWh
        }
