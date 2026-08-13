"""Custom exception hierarchy for the Continuous Learning & Shared Experience Engine."""


class LearningError(Exception):
    """Base class for all Learning Engine errors."""


class ExperienceNotFoundError(LearningError):
    """Raised when a requested experience record cannot be located."""


class PatternDetectionError(LearningError):
    """Raised when the pattern detector encounters an unrecoverable scan error."""


class StrategyNotFoundError(LearningError):
    """Raised when no strategy matches the requested domain or identifier."""


class RecommendationError(LearningError):
    """Raised when the recommendation engine fails to produce a valid result."""


class AgentExperienceError(LearningError):
    """Raised when agent-level experience data is missing or corrupted."""


class LessonExtractionError(LearningError):
    """Raised when lesson extraction fails for a given experience record."""
