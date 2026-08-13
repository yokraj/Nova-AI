"""Estimation Engine calculates task duration figures.
"""

from app.agents.software_engineer.project_manager.interfaces import IEstimationEngine
from app.agents.software_engineer.project_manager.models import Estimate, Task

class LocalEstimationEngine(IEstimationEngine):
    """Provides hour calculations using complexity criteria heuristics."""

    def estimate_task(self, task: Task) -> Estimate:
        """Determines estimated hours needed for different engineering activities."""
        desc = task.description.lower()
        
        # Base hours estimation factors
        dev = 8.0
        test = 2.0
        doc = 1.0
        deploy = 0.5

        if "database" in desc or "schema" in desc:
            dev = 4.0
            test = 1.0
            doc = 0.5
            deploy = 0.5
        elif "auth" in desc or "security" in desc:
            dev = 12.0
            test = 4.0
            doc = 2.0
            deploy = 1.0
        elif "documentation" in desc or "readme" in desc:
            dev = 1.0
            test = 0.5
            doc = 6.0
            deploy = 0.5

        total = dev + test + doc + deploy
        
        estimate = Estimate(
            dev_hours=dev,
            test_hours=test,
            doc_hours=doc,
            deploy_hours=deploy,
            total_hours=total
        )
        task.estimate = estimate
        return estimate
