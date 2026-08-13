"""Health Checker verifies model status using runtime health monitors.
"""

from typing import Optional
from app.ai.runtime.health import LocalHealthMonitor
from app.ai.runtime.registry import LocalModelRegistry
from app.ai.runtime.providers.ollama import OllamaLocalProvider

class RouterHealthChecker:
    """Interaces with local runtime health profiles."""

    def __init__(self, monitor: Optional[LocalHealthMonitor] = None) -> None:
        registry = LocalModelRegistry()
        provider = OllamaLocalProvider()
        self.monitor = monitor or LocalHealthMonitor(registry=registry, provider=provider)

    async def is_model_available(self, model_name: str) -> bool:
        """Determines if the model is downloaded and the inference server is online."""
        try:
            status = await self.monitor.get_overall_health()
            if not status.get("is_healthy", False):
                return False
            
            # If Ollama has models list, verify downloaded
            model_info = self.monitor.registry.get_model(model_name)
            return model_info is not None
        except Exception:
            return False
