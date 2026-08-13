"""Priority Engine assigns criticalities to tasks based on business and tech factors.
"""

from typing import List
from app.agents.software_engineer.project_manager.models import Task

class PriorityEngine:
    """Calculates hierarchy priority rankings (Critical, High, Medium, Low)."""

    def prioritize_tasks(self, tasks: List[Task]) -> List[Task]:
        """Scans task criteria to assign appropriate priority levels."""
        for task in tasks:
            desc = task.description.lower()
            
            # Simple heuristic priority checks
            if "auth" in desc or "schema" in desc or "database" in desc:
                task.priority = "Critical"
            elif "api" in desc or "endpoint" in desc or "integration" in desc:
                task.priority = "High"
            elif "documentation" in desc or "readme" in desc or "guide" in desc:
                task.priority = "Low"
            else:
                task.priority = "Medium"
        return tasks
