"""Custom exceptions for the Autonomous Software Engineer Integration Engine.
"""

class AutonomousError(Exception):
    """Base exception class for all autonomous integration engine errors."""
    pass

class WorkflowError(AutonomousError):
    """Raised when there is an error in workflow generation or structure."""
    pass

class PlanningError(AutonomousError):
    """Raised when solution design or implementation planning fails."""
    pass

class ExecutionError(AutonomousError):
    """Raised when a workflow task execution fails."""
    pass

class RoutingError(AutonomousError):
    """Raised when a request cannot be routed to a valid engine."""
    pass

class DecisionError(AutonomousError):
    """Raised when reasoning layer decision validation fails."""
    pass

class ValidationError(AutonomousError):
    """Raised when quality gate checks or self validations fail."""
    pass

class RecoveryError(AutonomousError):
    """Raised when failure recovery strategies fail to execute or rollback."""
    pass
