"""Intelligent Model Router matching tasks with optimal models, fallbacks, and confidence scoring.
"""

from typing import Any, Dict, Optional
import time
from app.ai.models.interfaces import IModelRouter
from app.ai.models.model_registry import UniversalModelRegistry
from app.ai.models.models import (
    ModelCapability,
    ModelCategory,
    ModelMetadata,
    ModelRoutingRequest,
    ModelRoutingResponse,
)


class IntelligentModelRouter(IModelRouter):
    """Intelligent Model Router dynamically dispatching requests to optimal local/remote models."""

    def __init__(self, registry: UniversalModelRegistry) -> None:
        self.registry = registry

    async def route_request(self, request: ModelRoutingRequest) -> ModelRoutingResponse:
        """Determines best model ID and provider for request.

        Args:
            request: ModelRoutingRequest payload.

        Returns:
            ModelRoutingResponse decision.
        """
        start_time = time.time()
        selected_model: Optional[ModelMetadata] = None
        fallback_used = False

        # 1. Prefer explicitly requested model if registered
        if request.preferred_model:
            selected_model = self.registry.get_model(request.preferred_model)

        # 2. Match by category
        if not selected_model:
            selected_model = self.registry.find_best_model_for_category(request.task_category)

        # 3. Fallback to general coding or reasoning model
        if not selected_model:
            fallback_used = True
            selected_model = self.registry.find_best_model_for_category(ModelCategory.CODING) or self.registry.list_models()[0]

        elapsed_ms = (time.time() - start_time) * 1000.0

        return ModelRoutingResponse(
            request_id=request.request_id,
            selected_model_id=selected_model.model_id,
            provider_type=selected_model.provider_type,
            confidence_score=0.98 if not fallback_used else 0.85,
            fallback_used=fallback_used,
            latency_ms=elapsed_ms,
        )
