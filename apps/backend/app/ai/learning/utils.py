"""PEP 562 Lazy Import Utility Mapping for the Learning Engine package."""

import importlib
from typing import Any

_LAZY_MAP: dict = {
    # Core
    "LearningConfiguration": "app.ai.learning.configuration",
    # Models
    "Experience": "app.ai.learning.models",
    "ExperienceType": "app.ai.learning.models",
    "ExperienceOutcome": "app.ai.learning.models",
    "Lesson": "app.ai.learning.models",
    "LessonCategory": "app.ai.learning.models",
    "Pattern": "app.ai.learning.models",
    "Strategy": "app.ai.learning.models",
    "Recommendation": "app.ai.learning.models",
    "RecommendationTarget": "app.ai.learning.models",
    "AgentExperience": "app.ai.learning.models",
    "LearningMetrics": "app.ai.learning.models",
    # Interfaces
    "ILearningEngine": "app.ai.learning.interfaces",
    "IExperienceStore": "app.ai.learning.interfaces",
    "IStrategyRepository": "app.ai.learning.interfaces",
    "IRecommendationEngine": "app.ai.learning.interfaces",
    # Exceptions
    "LearningError": "app.ai.learning.exceptions",
    "ExperienceNotFoundError": "app.ai.learning.exceptions",
    "PatternDetectionError": "app.ai.learning.exceptions",
    "StrategyNotFoundError": "app.ai.learning.exceptions",
    "RecommendationError": "app.ai.learning.exceptions",
    "AgentExperienceError": "app.ai.learning.exceptions",
    "LessonExtractionError": "app.ai.learning.exceptions",
    # Storage
    "ExperienceStore": "app.ai.learning.experience_store",
    "ExperienceManager": "app.ai.learning.experience_manager",
    "LearningMemory": "app.ai.learning.memory",
    # Intelligence
    "PatternDetector": "app.ai.learning.pattern_detector",
    "StrategyRepository": "app.ai.learning.strategy_repository",
    "LessonExtractor": "app.ai.learning.lesson_extractor",
    "RecommendationEngine": "app.ai.learning.recommendation_engine",
    "AgentMemory": "app.ai.learning.agent_memory",
    "CollaborationLearning": "app.ai.learning.collaboration_learning",
    # Feedback
    "PlannerFeedback": "app.ai.learning.planner_feedback",
    "WorkflowFeedback": "app.ai.learning.workflow_feedback",
    "MissionFeedback": "app.ai.learning.mission_feedback",
    "SafetyFeedback": "app.ai.learning.safety_feedback",
    # Observability
    "LearningMetricsTracker": "app.ai.learning.metrics",
    "LearningHealthMonitor": "app.ai.learning.health",
    # Engine
    "LearningEngine": "app.ai.learning.learning_engine",
    "MockLearningProvider": "app.ai.learning.providers.mock_provider",
}


def lazy_import(name: str) -> Any:
    """Dynamically imports a mapped class or utility by name."""
    if name in _LAZY_MAP:
        module_path = _LAZY_MAP[name]
        module = importlib.import_module(module_path)
        return getattr(module, name)
    raise AttributeError(f"Attribute '{name}' not found in learning lazy mapping.")
