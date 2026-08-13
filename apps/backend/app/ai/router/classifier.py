"""Task Classification Engine parses input queries to determine TaskType.
"""

from app.ai.router.interfaces import ITaskClassifier
from app.ai.router.models import TaskType

class TaskClassifier(ITaskClassifier):
    """Detects task category using keyword rules."""

    def classify(self, prompt: str) -> TaskType:
        """Heuristically parses prompt content to return a matching TaskType."""
        desc = prompt.lower()

        if "fix" in desc or "error" in desc or "debug" in desc or "broken" in desc:
            return TaskType.DEBUGGING
        elif "refactor" in desc or "clean" in desc or "lint" in desc:
            return TaskType.REFACTORING
        elif "explain" in desc or "research" in desc or "what is" in desc or "how does" in desc:
            return TaskType.RESEARCH
        elif "embed" in desc or "vector" in desc or "similarity" in desc:
            return TaskType.EMBEDDING
        elif "look at" in desc or "image" in desc or "vision" in desc:
            return TaskType.VISION
        elif "plan" in desc or "architecture" in desc or "sprint" in desc or "design" in desc:
            return TaskType.PLANNING
        elif "generate" in desc or "create" in desc or "write" in desc or "build" in desc:
            return TaskType.CODE_GENERATION
        else:
            return TaskType.CHAT
