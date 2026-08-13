"""Autonomous Self-Improvement & Adaptive Intelligence Engine package.

Exposes configuration, models, interfaces, exceptions, PerformanceAnalyzer, WorkflowOptimizer, PlannerOptimizer,
AutomationOptimizer, MissionOptimizer, ConversationOptimizer, ResearchOptimizer, CopilotOptimizer,
VisionOptimizer, RuntimeOptimizer, AgentOptimizer, SkillEvolution, ExperienceDistiller, BehaviorOptimizer,
GoalOptimizer, AdaptiveEngine, BenchmarkEngine, FeedbackEngine, QualityEngine, KnowledgeRefiner,
LearningScheduler, SelfEvaluator, RecommendationEngine, observability, and UniversalSelfImprovementEngine.
"""

import sys
from typing import Any
from app.ai.self_improvement.utils import lazy_import

__all__ = [
    "SelfImprovementConfiguration",
    "OptimizationScope",
    "EvaluationCycle",
    "RegressionStatus",
    "OptimizationStatus",
    "PerformanceMetricsSnapshot",
    "AgentScorecard",
    "ExperiencePackage",
    "WorkflowOptimizationRecommendation",
    "BenchmarkReport",
    "QualityDiagnosticReport",
    "SelfImprovementHealth",
    "SelfImprovementMetrics",
    "IPerformanceAnalyzer",
    "IWorkflowOptimizer",
    "IExperienceDistiller",
    "IBenchmarkEngine",
    "IQualityEngine",
    "ISelfImprovementManager",
    "IUniversalSelfImprovementEngine",
    "SelfImprovementEngineError",
    "OptimizationFailedError",
    "RegressionDetectedError",
    "DistillationError",
    "PerformanceAnalyzer",
    "WorkflowOptimizer",
    "PlannerOptimizer",
    "AutomationOptimizer",
    "MissionOptimizer",
    "ConversationOptimizer",
    "ResearchOptimizer",
    "CopilotOptimizer",
    "VisionOptimizer",
    "RuntimeOptimizer",
    "AgentOptimizer",
    "SkillEvolution",
    "ExperienceDistiller",
    "BehaviorOptimizer",
    "GoalOptimizer",
    "AdaptiveEngine",
    "BenchmarkEngine",
    "FeedbackEngine",
    "QualityEngine",
    "KnowledgeRefiner",
    "LearningScheduler",
    "SelfEvaluator",
    "RecommendationEngine",
    "SelfImprovementMetricsTracker",
    "SelfImprovementHealthMonitor",
    "SelfImprovementCache",
    "MockSelfImprovementProvider",
    "SelfImprovementManager",
    "UniversalSelfImprovementEngine",
]


def __getattr__(name: str) -> Any:
    return lazy_import(name)
