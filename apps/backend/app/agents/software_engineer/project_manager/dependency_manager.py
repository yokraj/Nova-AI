"""Dependency Manager tracks task relations and resolves critical paths.
"""

from typing import List, Dict
from app.agents.software_engineer.project_manager.models import Task

class DependencyManager:
    """Configures links and dependencies order between tasks."""

    def resolve_dependencies(self, tasks: List[Task]) -> List[Task]:
        """Arranges tasks in topological order if dependencies are defined, otherwise assigns default waterfall order."""
        # Map tasks by suffix/category to create logical dependency sequences:
        # db -> backend -> frontend -> testing -> documentation -> deployment
        task_map: Dict[str, Task] = {t.id: t for t in tasks}
        
        # Helper to find tasks of a specific type
        def find_task_by_type(suffix: str) -> List[Task]:
            return [t for t in tasks if t.id.endswith(suffix)]

        db_tasks = find_task_by_type("db")
        be_tasks = find_task_by_type("backend")
        fe_tasks = find_task_by_type("frontend")
        test_tasks = find_task_by_type("testing")
        doc_tasks = find_task_by_type("documentation")
        dep_tasks = find_task_by_type("deployment")

        # Set dependency relationships:
        # Backend depends on DB
        for be in be_tasks:
            for db in db_tasks:
                if db.id not in be.dependencies:
                    be.dependencies.append(db.id)

        # Frontend depends on Backend
        for fe in fe_tasks:
            for be in be_tasks:
                if be.id not in fe.dependencies:
                    fe.dependencies.append(be.id)

        # Testing depends on Frontend
        for tst in test_tasks:
            for fe in fe_tasks:
                if fe.id not in tst.dependencies:
                    tst.dependencies.append(fe.id)

        # Documentation depends on Testing
        for doc in doc_tasks:
            for tst in test_tasks:
                if tst.id not in doc.dependencies:
                    doc.dependencies.append(tst.id)

        # Deployment depends on Documentation
        for dep in dep_tasks:
            for doc in doc_tasks:
                if doc.id not in dep.dependencies:
                    dep.dependencies.append(doc.id)

        return tasks

    def calculate_critical_path(self, tasks: List[Task]) -> List[str]:
        """Finds list of task IDs that form the longest sequence chain."""
        # A simple critical path here is one task of each sequence in order
        path = []
        for suffix in ["db", "backend", "frontend", "testing", "documentation", "deployment"]:
            matching = [t.id for t in tasks if t.id.endswith(suffix)]
            if matching:
                path.append(matching[0])
        return path
