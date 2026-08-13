"""Runtime Optimizer optimizing local model loading, GPU VRAM allocation, and CPU fallback rules.
"""

from typing import Any, Dict


class RuntimeOptimizer:
    """Optimizes local AI model loading order, VRAM allocation thresholds, and CPU fallback rules."""

    def optimize_vram_allocation(self, used_vram_mb: int, total_vram_mb: int) -> Dict[str, Any]:
        """Calculates VRAM allocation optimizations.

        Args:
            used_vram_mb: Currently allocated VRAM in MB.
            total_vram_mb: Total hardware VRAM in MB.

        Returns:
            Dictionary containing recommended model unload policy.
        """
        utilization_pct = (used_vram_mb / total_vram_mb) * 100.0
        return {
            "vram_utilization_pct": utilization_pct,
            "unload_policy": "aggressive_gc" if utilization_pct > 80.0 else "lazy_gc",
            "cpu_fallback_threshold_mb": total_vram_mb - 1024,
        }
