"""Custom exception hierarchy for Autonomous Self-Improvement & Adaptive Intelligence Engine.
"""


class SelfImprovementEngineError(Exception):
    """Base exception for all Self-Improvement Engine errors."""

    pass


class OptimizationFailedError(SelfImprovementEngineError):
    """Raised when a workflow or agent optimization fails to apply."""

    pass


class RegressionDetectedError(SelfImprovementEngineError):
    """Raised when a performance or accuracy regression is detected."""

    pass


class DistillationError(SelfImprovementEngineError):
    """Raised when experience distillation fails."""

    pass
