"""PromptValidator verifying variables completeness and limits checks.
"""

import re
from typing import Any, Dict

from app.agent_sdk.prompt.exceptions import PromptValidationError
from app.agent_sdk.prompt.prompt import Prompt


class PromptValidator:
    """Validates prompt structure, placeholders, and variables consistency."""

    def validate(self, prompt: Prompt, variables: Dict[str, Any], max_size: int = 100000) -> None:
        """Validates variables and placeholders consistency.

        Args:
            prompt: Prompt definition.
            variables: Dict of variables to render.
            max_size: Maximum size limit for rendered text.

        Raises:
            PromptValidationError: If validation checks fail.
        """
        combined = prompt.system_prompt + prompt.user_prompt

        # Validate placeholder match format boundaries
        if re.search(r"\{\{[^}]*$", combined) or re.search(r"^[^{]*\}\}", combined):
            raise PromptValidationError("Prompt template contains malformed placeholders.")

        # Check missing declared variables
        missing = [var for var in prompt.variables if var not in variables]
        if missing:
            raise PromptValidationError(f"Missing required variables: {', '.join(missing)}")

        # Check size constraints
        est_size = len(prompt.system_prompt) + len(prompt.user_prompt)
        for val in variables.values():
            est_size += len(str(val))
        if est_size > max_size:
            raise PromptValidationError(f"Estimated prompt size ({est_size}) exceeds limit ({max_size}).")
