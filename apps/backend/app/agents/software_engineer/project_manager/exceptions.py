"""Custom exceptions for the Enterprise Software Project Manager Engine.
"""

class ProjectError(Exception):
    """Base exception class for all Project Manager Engine errors."""
    pass

class RequirementError(ProjectError):
    """Raised when there is an error analyzing or parsing requirements."""
    pass

class PlanningError(ProjectError):
    """Raised when there is an error planning the project roadmap or milestone alignment."""
    pass

class TaskGenerationError(ProjectError):
    """Raised when there is an error generating or decomposing tasks."""
    pass

class EstimationError(ProjectError):
    """Raised when task estimation calculations fail."""
    pass

class DependencyError(ProjectError):
    """Raised when a dependency conflict or deadlock is detected."""
    pass

class RiskAnalysisError(ProjectError):
    """Raised when risk identification or mitigation planning fails."""
    pass

class ReportError(ProjectError):
    """Raised when generating project or sprint reports fails."""
    pass

class ValidationError(ProjectError):
    """Raised when validating project schemas or states fails."""
    pass
