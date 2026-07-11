"""PromptRenderer replacing variables dynamically in prompt templates.
"""

import re
from typing import Any, Dict

from app.agent_sdk.prompt.exceptions import PromptRenderingError


class PromptRenderer:
    """Renders variables into templates, supporting recursive nested evaluations."""

    def render(self, template_str: str, variables: Dict[str, Any], max_depth: int = 5) -> str:
        """Replaces {{variable}} placeholders recursively.

        Args:
            template_str: Template string.
            variables: Dict of variable keys and values.
            max_depth: Maximum recursion depth for nested variables.

        Returns:
            Rendered string.

        Raises:
            PromptRenderingError: If recursion exceeds max depth.
        """
        pattern = re.compile(r"\{\{\s*(\w+)\s*\}\}")
        current = template_str

        for _ in range(max_depth):
            matches = pattern.findall(current)
            if not matches:
                return current

            has_replaced = False
            for match in matches:
                if match in variables:
                    val = str(variables[match])
                    current = current.replace(f"{{{{{match}}}}}", val)
                    has_replaced = True

            if not has_replaced:
                break
        else:
            raise PromptRenderingError("Nested variable substitution exceeded maximum recursion depth.")

        return current
