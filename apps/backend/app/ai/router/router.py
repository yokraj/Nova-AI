"""Main Intelligent Model Router orchestrator.
"""

from typing import Optional
from app.ai.router.interfaces import IModelRouter
from app.ai.router.models import RoutingRequest, RoutingDecision, TaskType
from app.ai.router.classifier import TaskClassifier
from app.ai.router.task_analyzer import TaskAnalyzer
from app.ai.router.model_selector import ModelSelector
from app.ai.router.health_checker import RouterHealthChecker
from app.ai.router.resource_monitor import ResourceMonitor
from app.ai.router.cost_optimizer import CostOptimizer
from app.ai.router.fallback_manager import FallbackManager

class IntelligentModelRouter(IModelRouter):
    """Orchestrates classification, resource bounds check, model ranking, selection, and fallbacks."""

    def __init__(
        self,
        classifier: Optional[TaskClassifier] = None,
        analyzer: Optional[TaskAnalyzer] = None,
        selector: Optional[ModelSelector] = None,
        health: Optional[RouterHealthChecker] = None,
        monitor: Optional[ResourceMonitor] = None,
        optimizer: Optional[CostOptimizer] = None,
        fallback_mgr: Optional[FallbackManager] = None
    ) -> None:
        self.classifier = classifier or TaskClassifier()
        self.analyzer = analyzer or TaskAnalyzer()
        self.selector = selector or ModelSelector()
        self.health = health or RouterHealthChecker()
        self.monitor = monitor or ResourceMonitor()
        self.optimizer = optimizer or CostOptimizer()
        self.fallback_mgr = fallback_mgr or FallbackManager()

    async def route_request(self, request: RoutingRequest) -> RoutingDecision:
        """Executes the intelligent routing pipeline from request parameters to final selection."""
        # 1. Classification
        if not request.task_type:
            request.task_type = self.classifier.classify(request.prompt)

        # 2. Complexity Analysis
        profile = self.analyzer.analyze_request(request)

        # 3. Model Ranking & Selection
        decision = self.selector.select_best_model(request)

        # 4. Resource Check
        self.monitor.check_resource_limits(decision.selected_model)

        # 5. Cost Optimization
        local_up = await self.health.is_model_available(decision.selected_model)
        decision = self.optimizer.optimize_decision(decision, local_up)

        return decision

    def handle_execution_failure(self, decision: RoutingDecision, failed_model: str) -> str:
        """Resolves the fallback model if a selected model fails during execution."""
        return self.fallback_mgr.resolve_next_model(decision, failed_model)
