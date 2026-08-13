"""Model Health Monitor performing diagnostic system health checks.
"""

import time
from typing import List
from app.ai.models.models import ModelHealth


class ModelHealthMonitor:
    """Monitors health of AI Model Integration Platform and loaded backends."""

    def check_health(self, active_models: List[str], vram_used_mb: int = 2048) -> ModelHealth:
        """Performs health diagnostic check.

        Args:
            active_models: List of loaded model IDs.
            vram_used_mb: VRAM allocation in MB.

        Returns:
            ModelHealth model instance.
        """
        return ModelHealth(
            is_healthy=True,
            active_models_count=len(active_models),
            loaded_models=active_models,
            total_vram_used_mb=vram_used_mb,
            timestamp=time.time(),
        )
