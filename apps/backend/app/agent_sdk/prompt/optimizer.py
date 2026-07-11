"""PromptOptimizer compressing formatting and fitting context windows.
"""

import re
from typing import Any, Dict, List

from app.agent_sdk.prompt.prompt import Prompt


class PromptOptimizer:
    """Optimizes and compresses prompts to fit context windows."""

    def compress_whitespace(self, text: str) -> str:
        """Replaces consecutive spaces and blank lines with single formatting.

        Args:
            text: Input string.

        Returns:
            Compressed string.
        """
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n+", "\n", text)
        return text.strip()

    def remove_duplicate_context(self, text: str) -> str:
        """Removes duplicate lines from context blocks to save tokens.

        Args:
            text: Input context string.

        Returns:
            Deduplicated string.
        """
        lines = text.split("\n")
        seen = set()
        deduped = []
        for line in lines:
            trimmed = line.strip()
            if trimmed:
                if trimmed not in seen:
                    seen.add(trimmed)
                    deduped.append(line)
            else:
                deduped.append(line)
        return "\n".join(deduped)

    def trim_history(self, history: List[Dict[str, str]], max_turns: int = 5) -> List[Dict[str, str]]:
        """Trims chat history turns list to fit budget.

        Args:
            history: List of dialog turns.
            max_turns: Maximum turns count to preserve.

        Returns:
            Trimmed history list.
        """
        if len(history) <= max_turns:
            return history
        first_turn = history[0]
        if first_turn.get("role") == "system":
            return [first_turn] + list(history[-(max_turns - 1) :])
        return list(history[-max_turns:])

    def fit_context_window(
        self, prompt: Prompt, variables: Dict[str, Any], context_limit: int = 4096
    ) -> Dict[str, Any]:
        """Truncates text inputs in variables to prevent window overflow.

        Args:
            prompt: The Prompt target.
            variables: Dict of variables to render.
            context_limit: Context budget limit in tokens (approx 4 chars/token).

        Returns:
            Optimized variables dictionary.
        """
        system_len = len(prompt.system_prompt)
        user_len = len(prompt.user_prompt)

        char_limit = context_limit * 4
        available_chars = char_limit - system_len - user_len
        if available_chars <= 0:
            return variables

        optimized_vars = {}
        for key, val in variables.items():
            val_str = str(val)
            if len(val_str) > available_chars and (
                key == "code" or key == "clipboard" or key == "selected_text"
            ):
                optimized_vars[key] = val_str[:available_chars] + "\n... [TRUNCATED] ..."
            else:
                optimized_vars[key] = val
        return optimized_vars
