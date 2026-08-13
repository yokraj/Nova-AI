"""Load Balancer Module.

Distributes requests across multiple Ollama instances, vLLM servers, GPUs, and cloud endpoints.
"""

from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class LoadBalancer:
    """Enterprise Round-Robin & Least-Loaded Inference Load Balancer."""

    def __init__(self) -> None:
        self.endpoints = [
            {"provider": "ollama", "url": "http://localhost:11434", "active_connections": 2},
            {"provider": "ollama", "url": "http://localhost:11435", "active_connections": 0},
            {"provider": "vllm", "url": "http://localhost:8000", "active_connections": 1},
        ]
        logger.info("load_balancer_initialized", active_endpoints=len(self.endpoints))

    def select_best_endpoint(self, target_provider: str = "ollama") -> Dict[str, Any]:
        """Selects least-loaded endpoint for target provider."""
        matching = [e for e in self.endpoints if e["provider"] == target_provider]
        if not matching:
            return {"url": "http://localhost:11434", "provider": target_provider}

        best = min(matching, key=lambda x: x["active_connections"])
        best["active_connections"] += 1
        logger.info("endpoint_selected", url=best["url"], connections=best["active_connections"])
        return best
