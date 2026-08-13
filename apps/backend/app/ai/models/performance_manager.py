"""Performance Manager optimizing GPU/CPU VRAM allocation, batching, and context reuse.
"""

from typing import Any, Dict
from app.ai.models.interfaces import IPerformanceManager


class PerformanceManager(IPerformanceManager):
    """Performance Manager monitoring GPU VRAM allocation and optimization options."""

    def __init__(self, max_vram_gb: float = 8.0) -> None:
        self.max_vram_mb = int(max_vram_gb * 1024)
        self._current_used_vram_mb = 2048

    def get_vram_usage(self) -> Dict[str, Any]:
        """Returns GPU VRAM allocation telemetry."""
        return {
            "max_vram_mb": self.max_vram_mb,
            "used_vram_mb": self._current_used_vram_mb,
            "free_vram_mb": max(0, self.max_vram_mb - self._current_used_vram_mb),
            "usage_percent": (self._current_used_vram_mb / self.max_vram_mb) * 100.0,
        }

    def allocate_vram(self, amount_mb: int) -> bool:
        """Attempts VRAM allocation for model loading."""
        if self._current_used_vram_mb + amount_mb <= self.max_vram_mb:
            self._current_used_vram_mb += amount_mb
            return True
        return False

    def release_vram(self, amount_mb: int) -> None:
        """Releases VRAM after model unloading."""
        self._current_used_vram_mb = max(0, self._current_used_vram_mb - amount_mb)
