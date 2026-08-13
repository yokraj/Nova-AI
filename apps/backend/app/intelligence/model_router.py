"""Model Router Module.

Dynamically routes inference requests to local models (Ollama, llama.cpp, vLLM) or optional cloud endpoints
(OpenAI / Anthropic compatible APIs) based on task requirements, latency bounds, and offline policies.
"""

from typing import Any, Dict, Optional
import structlog

from app.intelligence.config import IntelligenceConfig, ModelProviderConfig
from app.intelligence.exceptions import ModelRoutingError

logger = structlog.get_logger(__name__)


class ModelRouter:
    """Enterprise LLM Model Routing & Endpoint Orchestrator."""

    def __init__(self, config: Optional[IntelligenceConfig] = None) -> None:
        self.config = config or IntelligenceConfig()
        logger.info("model_router_initialized", default_provider=self.config.default_provider)

    def select_model(self, task_type: str = "general", prefer_local: bool = True) -> Dict[str, Any]:
        """Dynamically selects optimal model tag and provider config based on task requirements."""
        task_lower = task_type.lower()
        
        # 1. Routing Decision Matrix
        if "code" in task_lower or "programming" in task_lower:
            selected_model = self.config.coding_model
            provider_id = "ollama"
        elif "reason" in task_lower or "logic" in task_lower or "math" in task_lower:
            selected_model = self.config.reasoning_model
            provider_id = "ollama"
        elif "fast" in task_lower or "intent" in task_lower:
            selected_model = self.config.fast_model
            provider_id = "ollama"
        else:
            selected_model = self.config.default_model
            provider_id = self.config.default_provider

        # 2. Local vs Cloud Preference Check
        provider_cfg = self.config.providers.get(provider_id)
        if not provider_cfg:
            provider_cfg = ModelProviderConfig(provider_id="ollama")

        if prefer_local and not provider_cfg.is_local:
            # Fallback to local Ollama provider if local execution is enforced
            provider_id = "ollama"
            provider_cfg = self.config.providers.get("ollama", provider_cfg)

        logger.info(
            "model_selected",
            task_type=task_type,
            selected_model=selected_model,
            provider_id=provider_id,
            is_local=provider_cfg.is_local,
        )

        return {
            "provider_id": provider_id,
            "model": selected_model,
            "base_url": provider_cfg.base_url,
            "timeout_seconds": provider_cfg.timeout_seconds,
            "is_local": provider_cfg.is_local,
        }

    async def execute_inference(self, prompt: str, task_type: str = "general", **kwargs: Any) -> str:
        """Executes LLM inference via selected provider or local fallback simulation."""
        target = self.select_model(task_type=task_type)
        logger.debug("executing_inference", target=target, prompt_len=len(prompt))

        # Simulated high-performance local/cloud inference execution wrapper
        return f"[Generated Response using {target['model']} via {target['provider_id']}] Answer to prompt: {prompt[:80]}..."
