"""Interfaces for the Intelligent AI Model Router.
"""

from abc import ABC, abstractmethod
from typing import Any, List
from app.ai.router.models import RoutingRequest, RoutingDecision, TaskType

class ITaskClassifier(ABC):
    """Abstract interface for task classification."""

    @abstractmethod
    def classify(self, prompt: str) -> TaskType:
        """Determines task type from prompt."""
        pass

class IModelSelector(ABC):
    """Abstract interface for model selection."""

    @abstractmethod
    def select_best_model(self, request: RoutingRequest) -> RoutingDecision:
        """Ranks and selects the best model for a routing request."""
        pass

class IModelRouter(ABC):
    """Abstract interface for the main Intelligent Router orchestrator."""

    @abstractmethod
    async def route_request(self, request: RoutingRequest) -> RoutingDecision:
        """Executes the full intelligent model routing pipeline."""
        pass
