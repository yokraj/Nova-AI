"""Central Universal Self-Improvement Engine facade unifying workflow optimization, benchmarks, and experience distillation.
"""

import time
from typing import Any, Dict, List, Optional
from app.ai.self_improvement.adaptive_engine import AdaptiveEngine
from app.ai.self_improvement.agent_optimizer import AgentOptimizer
from app.ai.self_improvement.automation_optimizer import AutomationOptimizer
from app.ai.self_improvement.behavior_optimizer import BehaviorOptimizer
from app.ai.self_improvement.benchmark_engine import BenchmarkEngine
from app.ai.self_improvement.cache import SelfImprovementCache
from app.ai.self_improvement.configuration import SelfImprovementConfiguration
from app.ai.self_improvement.conversation_optimizer import ConversationOptimizer
from app.ai.self_improvement.copilot_optimizer import CopilotOptimizer
from app.ai.self_improvement.experience_distiller import ExperienceDistiller
from app.ai.self_improvement.feedback_engine import FeedbackEngine
from app.ai.self_improvement.goal_optimizer import GoalOptimizer
from app.ai.self_improvement.health import SelfImprovementHealthMonitor
from app.ai.self_improvement.interfaces import IUniversalSelfImprovementEngine
from app.ai.self_improvement.knowledge_refiner import KnowledgeRefiner
from app.ai.self_improvement.learning_scheduler import LearningScheduler
from app.ai.self_improvement.manager import SelfImprovementManager
from app.ai.self_improvement.metrics import SelfImprovementMetricsTracker
from app.ai.self_improvement.mission_optimizer import MissionOptimizer
from app.ai.self_improvement.models import (
    ExperiencePackage,
    SelfImprovementHealth,
    SelfImprovementMetrics,
)
from app.ai.self_improvement.performance_analyzer import PerformanceAnalyzer
from app.ai.self_improvement.planner_optimizer import PlannerOptimizer
from app.ai.self_improvement.quality_engine import QualityEngine
from app.ai.self_improvement.recommendation_engine import RecommendationEngine
from app.ai.self_improvement.research_optimizer import ResearchOptimizer
from app.ai.self_improvement.runtime_optimizer import RuntimeOptimizer
from app.ai.self_improvement.self_evaluator import SelfEvaluator
from app.ai.self_improvement.skill_evolution import SkillEvolution
from app.ai.self_improvement.vision_optimizer import VisionOptimizer
from app.ai.self_improvement.workflow_optimizer import WorkflowOptimizer


class UniversalSelfImprovementEngine(IUniversalSelfImprovementEngine):
    """The central Autonomous Self-Improvement & Adaptive Intelligence Platform runtime for Nova AI."""

    def __init__(self, config: Optional[SelfImprovementConfiguration] = None) -> None:
        self.config = config or SelfImprovementConfiguration()
        self.manager = SelfImprovementManager(self.config)
        self.performance_analyzer = PerformanceAnalyzer()
        self.workflow_optimizer = WorkflowOptimizer()
        self.planner_optimizer = PlannerOptimizer()
        self.automation_optimizer = AutomationOptimizer()
        self.mission_optimizer = MissionOptimizer()
        self.conversation_optimizer = ConversationOptimizer()
        self.research_optimizer = ResearchOptimizer()
        self.copilot_optimizer = CopilotOptimizer()
        self.vision_optimizer = VisionOptimizer()
        self.runtime_optimizer = RuntimeOptimizer()
        self.agent_optimizer = AgentOptimizer()
        self.skill_evolution = SkillEvolution()
        self.experience_distiller = ExperienceDistiller()
        self.behavior_optimizer = BehaviorOptimizer()
        self.goal_optimizer = GoalOptimizer()
        self.adaptive_engine = AdaptiveEngine()
        self.benchmark_engine = BenchmarkEngine()
        self.feedback_engine = FeedbackEngine()
        self.quality_engine = QualityEngine()
        self.knowledge_refiner = KnowledgeRefiner()
        self.learning_scheduler = LearningScheduler()
        self.self_evaluator = SelfEvaluator()
        self.recommendation_engine = RecommendationEngine()

        self.metrics_tracker = SelfImprovementMetricsTracker()
        self.health_monitor = SelfImprovementHealthMonitor()
        self.cache = SelfImprovementCache(ttl_seconds=self.config.cache_ttl_seconds)

        self._distilled_packages: List[ExperiencePackage] = []

    async def self_improve(self) -> Dict[str, Any]:
        """Runs full system-wide self-improvement evaluation pass."""
        self.metrics_tracker.record_evaluation()
        eval_result = self.self_evaluator.evaluate_self()
        adaptations = self.adaptive_engine.apply_adaptive_rules()

        # Distill sample workflow experience if enabled
        if self.config.auto_distill_workflows:
            pkg = self.experience_distiller.distill_experience("Build E-Commerce API", ["Requirement Analysis", "FastAPI Codegen", "Pytest Verification"])
            self._distilled_packages.append(pkg)
            self.metrics_tracker.record_experience_distillation()

        self.metrics_tracker.record_optimization()
        return {
            "status": "SUCCESS",
            "evaluations": eval_result,
            "adaptations": adaptations,
            "experiences_distilled": len(self._distilled_packages),
        }

    async def performance_report(self) -> Dict[str, Any]:
        """Retrieves performance report across core subsystems."""
        perf_kernel = self.performance_analyzer.analyze_subsystem("kernel")
        perf_copilot = self.performance_analyzer.analyze_subsystem("copilot")
        return {
            "kernel": perf_kernel.model_dump(mode="json"),
            "copilot": perf_copilot.model_dump(mode="json"),
            "user_rating": self.feedback_engine.get_average_rating(),
        }

    async def workflow_recommendations(self) -> List[Dict[str, Any]]:
        """Retrieves system optimization recommendations."""
        return self.recommendation_engine.generate_system_recommendations()

    async def agent_scorecard(self) -> List[Dict[str, Any]]:
        """Retrieves evaluation scorecards for agent workforce."""
        cards = self.agent_optimizer.evaluate_agents()
        return [c.model_dump(mode="json") for c in cards]

    async def benchmark_report(self) -> Dict[str, Any]:
        """Retrieves benchmark evaluation report."""
        report = self.benchmark_engine.run_benchmark()
        return report.model_dump(mode="json")

    async def quality_report(self) -> Dict[str, Any]:
        """Retrieves quality diagnostic report."""
        report = self.quality_engine.check_quality()
        return report.model_dump(mode="json")

    async def adaptive_settings(self) -> Dict[str, Any]:
        """Retrieves active adaptive behavior settings."""
        style = self.behavior_optimizer.adapt_behavior_style(user_interaction_count=15)
        profile = self.goal_optimizer.get_user_profile()
        return {"style": style, "profile": profile}

    async def experience_summary(self) -> Dict[str, Any]:
        """Retrieves summary of distilled experience packages."""
        return {
            "total_packages": len(self._distilled_packages),
            "packages": [p.model_dump(mode="json") for p in self._distilled_packages],
        }

    async def check_health(self) -> SelfImprovementHealth:
        """Retrieves self-improvement engine health diagnostics."""
        metrics = self.metrics_tracker.get_metrics()
        return self.health_monitor.check_health(metrics.optimizations_applied, metrics.total_evaluations)

    async def get_metrics(self) -> SelfImprovementMetrics:
        """Retrieves telemetry metrics."""
        return self.metrics_tracker.get_metrics()
