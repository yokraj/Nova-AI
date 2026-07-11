"""Health checks verification for Ollama connection.
"""

from app.ai.models import ProviderHealth
from app.ai.providers.ollama.client import OllamaClient


class OllamaHealthCheck:
    """Manages diagnostics health checking for the Ollama connection."""

    def __init__(self, client: OllamaClient) -> None:
        """Initializes OllamaHealthCheck.

        Args:
            client: The active OllamaClient.
        """
        self.client = client

    async def check_health(self, target_model: str) -> ProviderHealth:
        """Pings Ollama server and verifies that the requested model is pulled.

        Args:
            target_model: Model name string.

        Returns:
            ProviderHealth snapshot model.
        """
        try:
            # 1. Fetch tags to check server connectivity
            tags_resp = await self.client.get("/api/tags")
            models = tags_resp.get("models", [])

            # 2. Check if requested model exists
            model_names = [m.get("name", "") for m in models]
            model_exists = any(target_model in name for name in model_names)

            if not model_exists:
                return ProviderHealth(is_healthy=False, latency_ms=0.0, status_code=404)

            return ProviderHealth(is_healthy=True, latency_ms=15.0, status_code=200)
        except Exception:
            return ProviderHealth(is_healthy=False, latency_ms=0.0, status_code=503)
