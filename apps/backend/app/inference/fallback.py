"""Fallback Engine Module.

Implements multi-tier failover: Retry -> Switch provider -> Switch model -> Reduce context -> CPU fallback.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.inference.config import InferenceConfig
from app.inference.retry_manager import RetryManager

logger = structlog.get_logger(__name__)


class FallbackEngine:
    """Enterprise Multi-Tier Failover Engine."""

    def __init__(
        self,
        config: Optional[InferenceConfig] = None,
        retry_manager: Optional[RetryManager] = None,
    ) -> None:
        self.config = config or InferenceConfig()
        self.retry_manager = retry_manager or RetryManager(config=self.config)
        logger.info("fallback_engine_initialized")

    def execute_fallback_strategy(
        self, failed_provider: str, failed_model: str, prompt: str
    ) -> Dict[str, Any]:
        """Calculates fallback alternative provider, model, and context reduction.
        
        Enforces Zero-Cost Policy: Never falls back to commercial or paid cloud providers.
        Remains strictly within local Ollama models.
        """
        self.retry_manager.record_failure(failed_provider)

        # Hardened Local-Only Fallback Cascade
        # If a large local model fails, fallback to a lighter local Ollama model
        if failed_model in ("qwen3:8b", "llama3.1:70b", "deepseek-r1-distill-qwen"):
            fallback_provider = "ollama"
            fallback_model = "llama3.2"
        else:
            fallback_provider = "ollama"
            fallback_model = self.config.default_model

        logger.info(
            "local_fallback_strategy_triggered",
            original_provider=failed_provider,
            original_model=failed_model,
            fallback_provider=fallback_provider,
            fallback_model=fallback_model,
        )
        return {
            "fallback_provider": fallback_provider,
            "fallback_model": fallback_model,
            "reduce_context": True,
            "cpu_fallback": True,
        }
