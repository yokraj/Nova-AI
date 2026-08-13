"""Resource Monitor validates system resources boundaries.
"""

from typing import Dict
from app.ai.router.exceptions import ResourceLimitError

class ResourceMonitor:
    """Tracks CPU, RAM, and GPU memory metrics, enforcing size constraints."""

    def __init__(self, available_ram_gb: float = 16.0) -> None:
        self.available_ram_gb = available_ram_gb

    def check_resource_limits(self, model_name: str) -> None:
        """Raises ResourceLimitError if the model requires more memory than available."""
        # Simple size rule mappings
        model_size_mapping = {
            "qwen2.5-coder": 6.0,          # 7B fits in 6GB
            "deepseek-r1-distill-qwen": 8.0, # 8B fits in 8GB
            "llama3": 6.0,                 # 8B fits in 6GB
            "nomic-embed-text": 1.0,       # embedding fits in 1GB
            "qwen2.5-vl": 8.0              # 7B VL fits in 8GB
        }

        required = model_size_mapping.get(model_name, 8.0)
        if required > self.available_ram_gb:
            raise ResourceLimitError(
                f"Resource Limit Exceeded: Model '{model_name}' requires `{required}GB` memory, "
                f"but only `{self.available_ram_gb}GB` is available."
            )

    def get_system_usage(self) -> Dict[str, float]:
        """Returns dummy hardware usage stats."""
        return {
            "cpu_usage_pct": 35.0,
            "ram_usage_gb": 4.5,
            "gpu_vram_usage_gb": 2.1
        }
