"""Intelligent AI Model Router package exports.
"""

from app.ai.router.exceptions import (
    ModelRoutingError,
    ModelUnavailableError,
    NoSuitableModelError,
    FallbackExhaustedError,
    ResourceLimitError,
)
from app.ai.router.interfaces import ITaskClassifier, IModelSelector, IModelRouter
from app.ai.router.configuration import RouterConfiguration
from app.ai.router.models import TaskType, RoutingRequest, ModelScore, RoutingDecision, RoutingResult
from app.ai.router.classifier import TaskClassifier
from app.ai.router.task_analyzer import TaskAnalyzer, TaskProfile
from app.ai.router.complexity_estimator import ComplexityEstimator
from app.ai.router.model_selector import ModelSelector
from app.ai.router.routing_strategy import RoutingStrategy
from app.ai.router.fallback_manager import FallbackManager
from app.ai.router.health_checker import RouterHealthChecker
from app.ai.router.resource_monitor import ResourceMonitor
from app.ai.router.cost_optimizer import CostOptimizer
from app.ai.router.router import IntelligentModelRouter
from app.ai.router.cache import RouterCache
from app.ai.router.metrics import RouterMetricsTracker
from app.ai.router.utils import calculate_prompt_hash

__all__ = [
    "ModelRoutingError",
    "ModelUnavailableError",
    "NoSuitableModelError",
    "FallbackExhaustedError",
    "ResourceLimitError",
    "ITaskClassifier",
    "IModelSelector",
    "IModelRouter",
    "RouterConfiguration",
    "TaskType",
    "RoutingRequest",
    "ModelScore",
    "RoutingDecision",
    "RoutingResult",
    "TaskClassifier",
    "TaskAnalyzer",
    "TaskProfile",
    "ComplexityEstimator",
    "ModelSelector",
    "RoutingStrategy",
    "FallbackManager",
    "RouterHealthChecker",
    "ResourceMonitor",
    "CostOptimizer",
    "IntelligentModelRouter",
    "RouterCache",
    "RouterMetricsTracker",
    "calculate_prompt_hash",
]
