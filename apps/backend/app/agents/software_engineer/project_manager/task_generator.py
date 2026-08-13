"""Task Generator creates technical tasks for project features.
"""

from typing import List
from app.agents.software_engineer.project_manager.interfaces import ITaskGenerator
from app.agents.software_engineer.project_manager.models import Epic, Feature, Task, SubTask, Estimate

class LocalTaskGenerator(ITaskGenerator):
    """Generates lists of tasks mapped to development, testing, documentation, and deployment."""

    def generate_tasks_for_feature(self, feature: Feature) -> List[Task]:
        """Drafts standard task items based on feature characteristics."""
        clean_name = feature.name.replace(" ", "-").lower()
        tasks = [
            Task(
                id=f"task-{clean_name}-backend",
                title=f"Backend API for {feature.name}",
                description=f"Implement backend logic, services, and endpoints for {feature.name}.",
                estimate=Estimate(dev_hours=8.0, test_hours=2.0, doc_hours=1.0, deploy_hours=0.5, total_hours=11.5),
                subtasks=[
                    SubTask(id=f"subtask-{clean_name}-be-1", title="Write API handler router"),
                    SubTask(id=f"subtask-{clean_name}-be-2", title="Write business use-cases")
                ]
            ),
            Task(
                id=f"task-{clean_name}-db",
                title=f"Database schema for {feature.name}",
                description=f"Design database tables, indexes, and write migration scripts for {feature.name}.",
                estimate=Estimate(dev_hours=4.0, test_hours=1.0, doc_hours=0.5, deploy_hours=0.5, total_hours=6.0),
                subtasks=[
                    SubTask(id=f"subtask-{clean_name}-db-1", title="Write migrations scripts"),
                    SubTask(id=f"subtask-{clean_name}-db-2", title="Verify indexes optimization")
                ]
            ),
            Task(
                id=f"task-{clean_name}-frontend",
                title=f"Frontend integration for {feature.name}",
                description=f"Design UI interfaces and bind components with backend API for {feature.name}.",
                estimate=Estimate(dev_hours=10.0, test_hours=3.0, doc_hours=1.5, deploy_hours=0.5, total_hours=15.0),
                subtasks=[
                    SubTask(id=f"subtask-{clean_name}-fe-1", title="Design responsive screens"),
                    SubTask(id=f"subtask-{clean_name}-fe-2", title="Hook API endpoints client")
                ]
            ),
            Task(
                id=f"task-{clean_name}-testing",
                title=f"Testing verification for {feature.name}",
                description=f"Write pytest/jest test suites and execute regression testing for {feature.name}.",
                estimate=Estimate(dev_hours=2.0, test_hours=8.0, doc_hours=1.0, deploy_hours=0.5, total_hours=11.5),
                subtasks=[
                    SubTask(id=f"subtask-{clean_name}-test-1", title="Write unit testing files"),
                    SubTask(id=f"subtask-{clean_name}-test-2", title="Run integration validations")
                ]
            ),
            Task(
                id=f"task-{clean_name}-documentation",
                title=f"Documentation guides for {feature.name}",
                description=f"Draft technical API architecture diagrams and user user-guides for {feature.name}.",
                estimate=Estimate(dev_hours=1.0, test_hours=0.5, doc_hours=6.0, deploy_hours=0.5, total_hours=8.0),
                subtasks=[
                    SubTask(id=f"subtask-{clean_name}-doc-1", title="Draft OpenAPI definitions"),
                    SubTask(id=f"subtask-{clean_name}-doc-2", title="Update README workspace links")
                ]
            ),
            Task(
                id=f"task-{clean_name}-deployment",
                title=f"Deployment configuration for {feature.name}",
                description=f"Draft container configurations and CI pipelines adjustments for {feature.name}.",
                estimate=Estimate(dev_hours=1.0, test_hours=1.0, doc_hours=1.0, deploy_hours=4.0, total_hours=7.0),
                subtasks=[
                    SubTask(id=f"subtask-{clean_name}-dep-1", title="Adjust Dockerfile parameters"),
                    SubTask(id=f"subtask-{clean_name}-dep-2", title="Verify CI yaml files checks")
                ]
            )
        ]
        return tasks

    def decompose_feature(self, name: str, description: str) -> Epic:
        """Decomposes a major capability into an Epic -> Feature -> Task -> Subtask tree."""
        clean_name = name.lower().replace(" ", "-")
        # 1. Create sub-features
        feature_be = Feature(
            id=f"feature-{clean_name}-backend",
            name=f"{name} Core Backend",
            description=f"Backend infrastructure and processing workflows for {name}."
        )
        feature_fe = Feature(
            id=f"feature-{clean_name}-frontend",
            name=f"{name} Web Client UI",
            description=f"Web user interfaces screens for {name}."
        )

        # 2. Add tasks
        feature_be.tasks = self.generate_tasks_for_feature(feature_be)
        feature_fe.tasks = self.generate_tasks_for_feature(feature_fe)

        return Epic(
            id=f"epic-{clean_name}",
            name=name,
            description=description,
            features=[feature_be, feature_fe]
        )
