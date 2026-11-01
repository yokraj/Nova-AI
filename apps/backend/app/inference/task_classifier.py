"""Task Classifier Module for Nova AI Enterprise Core Intelligence.

Classifies incoming prompts into 10 canonical task categories:
1. Conversation
2. Mathematics
3. Logical reasoning
4. Programming
5. Knowledge retrieval
6. File operations
7. Research
8. Planning
9. Multimodal understanding
10. Automation

Also detects if a deterministic tool (such as DeterministicCalculator) can directly
and authoritatively resolve the request.
"""

import re
from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class TaskClassifier:
    """Enterprise Prompt Task Intent Classifier."""

    def __init__(self) -> None:
        logger.info("task_classifier_initialized")

    def classify_task(self, prompt: str) -> Dict[str, Any]:
        """Classifies task intent category based on structural patterns and vocabulary."""
        p_lower = prompt.lower().strip()

        # Check for deterministic arithmetic patterns
        math_ops_pattern = r"(?:\d+\s*(?:[\+\-\*\/\^\%]|multiplied\s+by|times|divided\s+by|plus|minus)\s*\d+)"
        is_math_expr = bool(re.search(math_ops_pattern, p_lower))
        is_math_word = any(
            k in p_lower
            for k in [
                "multiplied", "multiply", "product", "divided", "division", "quotient",
                "plus", "minus", "subtract", "addition", "calculate", "compute", "arithmetic",
                "square root", "sqrt", "factorial", "prime number", "is prime", "gcd", "lcm",
                "math", "equation", "formula", "algebra", "integral", "derivative"
            ]
        )

        # Check if the prompt is asking to evaluate/verify a claim or explain reasoning
        is_claim_evaluation = any(
            k in p_lower
            for k in [
                "claimed", "is that correct", "is this correct", "is it correct",
                "true or false", "correct or incorrect", "why or why not", "explain why"
            ]
        )

        if (is_math_expr or is_math_word) and not is_claim_evaluation:
            category = "Mathematics"
            is_deterministic = is_math_expr or any(op in p_lower for op in ["multiplied", "times", "divided", "plus", "minus", "calculate", "compute"])
        elif is_claim_evaluation:
            category = "Logical reasoning"
            is_deterministic = False
        elif any(k in p_lower for k in ["image", "picture", "photo", "look at screen", "screenshot", "visual", "vision"]):
            category = "Multimodal understanding"
            is_deterministic = False
        elif any(k in p_lower for k in ["automate", "launch app", "open app", "close app", "system control", "volume", "shutdown", "click", "keystroke"]):
            category = "Automation"
            is_deterministic = False
        elif any(k in p_lower for k in ["file", "directory", "folder", "read file", "write file", "delete file", "search files"]):
            category = "File operations"
            is_deterministic = False
        elif any(k in p_lower for k in ["paper", "research", "study", "scientific", "literature", "arxiv", "pubmed"]):
            category = "Research"
            is_deterministic = False
        elif any(k in p_lower for k in ["plan", "roadmap", "steps to", "workflow", "milestone", "strategy", "decompose"]):
            category = "Planning"
            is_deterministic = False
        elif any(k in p_lower for k in ["python", "code", "def ", "function", "class ", "script", "program", "decorator", "algorithm", "regex", "bug", "debug", "traceback", "compile", "sql"]):
            category = "Programming"
            is_deterministic = False
        elif any(k in p_lower for k in ["puzzle", "riddle", "paradox", "if all", "syllogism", "deduce", "deduction", "logical reasoning", "logic"]):
            category = "Logical reasoning"
            is_deterministic = False
        elif any(k in p_lower for k in ["what is", "who is", "explain", "describe", "tell me about", "history of", "definition of", "how does"]):
            category = "Knowledge retrieval"
            is_deterministic = False
        else:
            category = "Conversation"
            is_deterministic = False

        logger.info("task_classified", prompt_snippet=prompt[:35], category=category, is_deterministic=is_deterministic)
        return {
            "task_category": category,
            "is_deterministic_arithmetic": category == "Mathematics" and is_deterministic,
            "confidence": 0.95,
        }
