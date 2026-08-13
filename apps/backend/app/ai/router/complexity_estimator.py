"""Complexity Estimator rates task scope complexity levels.
"""

class ComplexityEstimator:
    """Classifies tasks into Simple, Medium, or Complex tiers."""

    def estimate_complexity(self, prompt: str, context_size: int) -> str:
        """Heuristically calculates task complexity tiers based on prompt content and context tokens."""
        desc = prompt.lower()

        # Complex tier indicators
        if "architecture" in desc or "repository analysis" in desc or "refactor" in desc or context_size > 8192:
            return "Complex"
        # Medium tier indicators
        elif "generate" in desc or "fix" in desc or "debug" in desc or "write" in desc:
            return "Medium"
        # Simple fallback
        else:
            return "Simple"
