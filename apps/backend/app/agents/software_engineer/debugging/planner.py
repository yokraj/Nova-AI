"""Debug Planner classifying traceback patterns to formulate diagnostic checklists.
"""

from typing import List
from app.agents.software_engineer.debugging.interfaces import DebugPlanner
from app.agents.software_engineer.debugging.models import DebugContext, DebugRequest


class WorkspaceDebugPlanner(DebugPlanner):
    """Decomposes error logs into diagnosis task lists."""

    def plan_debugging(
        self, request: DebugRequest, context: DebugContext
    ) -> List[str]:
        """Examines the traceback pattern to formulate target checks.

        Args:
            request: Active debug request parameters.
            context: Compiled workspace contexts parameters.

        Returns:
            List of diagnostic task items.
        """
        tb = request.traceback_str.lower()
        tasks = []

        if "syntaxerror" in tb:
            tasks.append("syntax_check")
        elif "importerror" in tb or "modulenotfound" in tb:
            tasks.append("import_validation")
            tasks.append("dependency_check")
        elif "connectionerror" in tb or "http" in tb or "timeout" in tb:
            tasks.append("api_validation")
        elif "sqlalchemy" in tb or "database" in tb or "operationalerror" in tb:
            tasks.append("database_check")
        else:
            tasks.append("runtime_check")
            tasks.append("root_cause_tracing")

        # Always append logic audits and repairs planning
        tasks.append("repair_planning")
        tasks.append("confidence_estimation")

        return tasks
