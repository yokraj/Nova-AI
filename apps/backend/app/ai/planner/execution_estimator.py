"""Execution Estimator estimating task cost metrics and timeouts.
"""

from app.ai.planner.models import Task, TimeEstimate, CostEstimate

class ExecutionEstimator:
    """Estimates CPU, RAM, duration, and token bounds for planned tasks."""

    def estimate_task(self, task: Task) -> None:
        """Populates time and cost estimation variables on target task."""
        seconds = 30.0
        if task.priority == "Critical":
            seconds = 60.0
        elif task.priority == "High":
            seconds = 45.0

        task.time_estimate = TimeEstimate(
            estimated_seconds=seconds,
            maximum_timeout_seconds=seconds * 3.0,
            confidence_score=0.85
        )

        task.cost_estimate = CostEstimate(
            cpu_cores=0.5,
            memory_mb=512,
            token_limit=4096,
            monetary_cents=0.5
        )
