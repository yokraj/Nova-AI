"""Task Decomposer converts large features into Epics, Features, Tasks, and Subtasks.
"""

from app.agents.software_engineer.project_manager.models import Epic, Feature, Task
from app.agents.software_engineer.project_manager.task_generator import LocalTaskGenerator

class TaskDecomposer:
    """Decomposes complex, large goals into structured task hierarchy trees."""

    def __init__(self) -> None:
        self.generator = LocalTaskGenerator()

    def decompose(self, feature_name: str, description: str) -> Epic:
        """Splits a major request into hierarchical Epic -> Feature -> Task -> Subtask structure."""
        return self.generator.decompose_feature(feature_name, description)
