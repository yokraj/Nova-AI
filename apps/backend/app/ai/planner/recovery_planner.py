"""Recovery Planner generating alternate path recovery plans.
"""

from typing import Dict
from app.ai.planner.models import DependencyGraph, RecoveryPlan

class RecoveryPlanner:
    """Configures alternate agents list and maximum retry attempts limits."""

    def generate_recovery_plans(self, graph: DependencyGraph) -> Dict[str, RecoveryPlan]:
        """Returns recovery mapping dictionary for each task."""
        plans = {}
        for node_id, task in graph.nodes.items():
            # Soft fallback to Software Engineer Agent if specialized agent fails
            fallback_list = ["software_engineer"]
            if task.assignment and task.assignment.agent_id == "software_engineer":
                fallback_list = ["manual_assignment"]

            plans[node_id] = RecoveryPlan(
                task_id=node_id,
                alternate_agent_ids=fallback_list,
                degraded_execution_params={"safety_buffer_timeout": 60.0},
                allow_retry=True,
                max_retries=3
            )
        return plans
