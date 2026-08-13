"""Custom Exception classes for the Planner and Decomposition subsystem.
"""

class PlannerError(Exception):
    """Base exception for all planning and decomposition errors."""
    pass

class GoalAnalysisError(PlannerError):
    """Raised when goal parameters or scope boundaries extraction fails."""
    pass

class DecompositionError(PlannerError):
    """Raised when recursive task decomposition limits are breached or templates fail to load."""
    pass

class CycleError(PlannerError):
    """Raised when cycle checks detect invalid back-edges in dependency graphs."""
    pass

class ValidationError(PlannerError):
    """Raised when planning structures (trees, DAGs) fail integrity checks."""
    pass

class RecoveryError(PlannerError):
    """Raised when recovery planner fail to compile alternate executors lists."""
    pass

class SchedulerError(PlannerError):
    """Raised when scheduling topological sorting batches encounters bottlenecks."""
    pass
