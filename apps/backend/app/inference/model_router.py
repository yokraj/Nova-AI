"""Model Router Module.

High-level model routing coordinator evaluating task classification, capability requirements,
and model selection.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.inference.task_classifier import TaskClassifier
from app.inference.capability_detector import CapabilityDetector
from app.inference.model_selector import ModelSelector

logger = structlog.get_logger(__name__)


class ModelRouter:
    """Enterprise Master Model Router Coordinator."""

    def __init__(
        self,
        task_classifier: Optional[TaskClassifier] = None,
        capability_detector: Optional[CapabilityDetector] = None,
        model_selector: Optional[ModelSelector] = None,
    ) -> None:
        self.task_classifier = task_classifier or TaskClassifier()
        self.capability_detector = capability_detector or CapabilityDetector()
        self.model_selector = model_selector or ModelSelector()
        logger.info("model_router_coordinator_initialized")

    def route_request(
        self, prompt: str, user_model: Optional[str] = None, user_provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """Runs classification, capability detection, and model routing."""
        task_res = self.task_classifier.classify_task(prompt)
        caps = self.capability_detector.detect_capabilities(prompt, task_res["task_category"])
        sel_res = self.model_selector.select_model(
            task_category=task_res["task_category"],
            required_capabilities=caps,
            user_model_override=user_model,
            user_provider_override=user_provider,
        )

        logger.info("request_routed", model=sel_res["model"], provider=sel_res["provider"], category=task_res["task_category"])
        return {
            "task_category": task_res["task_category"],
            "is_deterministic_arithmetic": task_res.get("is_deterministic_arithmetic", False),
            "detected_capabilities": caps,
            "selected_model": sel_res["model"],
            "selected_provider": sel_res["provider"],
            "routing_reason": sel_res["reason"],
        }
