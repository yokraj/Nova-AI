"""Task Analyzer calculates request profiles and token scopes.
"""

from pydantic import BaseModel
from app.ai.router.models import RoutingRequest
from app.ai.router.complexity_estimator import ComplexityEstimator

class TaskProfile(BaseModel):
    """Summarizes target task metrics and capabilities demands."""
    complexity: str
    context_size: int
    required_capability: str

class TaskAnalyzer:
    """Evaluates tokens size, code complexities, and capability requirements."""

    def __init__(self) -> None:
        self.estimator = ComplexityEstimator()

    def analyze_request(self, request: RoutingRequest) -> TaskProfile:
        """Determines task profile mapping context lengths and complexity levels."""
        complexity = self.estimator.estimate_complexity(request.prompt, request.context_size)
        
        # Simple capability derivation
        required_cap = "chat"
        t_type = request.task_type
        if t_type:
            from app.ai.router.models import TaskType
            if t_type == TaskType.EMBEDDING:
                required_cap = "embeddings"
            elif t_type == TaskType.VISION:
                required_cap = "vision"

        return TaskProfile(
            complexity=complexity,
            context_size=request.context_size,
            required_capability=required_cap
        )
