"""Local Model Router maps tasks to correct models.
"""

class LocalModelRouter:
    """Routes generation and embedding tasks to the appropriate model architecture."""

    def __init__(self) -> None:
        self.default_coding = "qwen2.5-coder"
        self.default_reasoning = "deepseek-r1-distill-qwen"
        self.default_embedding = "nomic-embed-text"
        self.default_vision = "qwen2.5-vl"

    def select_model_for_task(self, task_description: str) -> str:
        """Heuristically picks the best model based on prompt description keywords."""
        desc = task_description.lower()

        if "embed" in desc or "vector" in desc or "similarity" in desc:
            return self.default_embedding
        elif "explain" in desc or "reason" in desc or "solve" in desc or "architecture" in desc:
            return self.default_reasoning
        elif "fix" in desc or "code" in desc or "python" in desc or "bug" in desc or "refactor" in desc:
            return self.default_coding
        elif "image" in desc or "vision" in desc or "look at" in desc:
            return self.default_vision
        else:
            return self.default_coding
