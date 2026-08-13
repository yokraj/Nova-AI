"""Action Validator checking target executions patterns.
"""

import re
from typing import Dict, Any

class ActionValidator:
    """Blocks malicious script patterns or injection attempts in system commands."""

    def __init__(self) -> None:
        # Regex to block dangerous shell expansions or command injection patterns
        self.block_patterns = [
            re.compile(r";\s*rm\s+-rf"),
            re.compile(r"\|\s*bash"),
            re.compile(r"&&\s*rm")
        ]

    def validate_action(self, action: str, parameters: Dict[str, Any]) -> bool:
        """Returns True if the action is safe to run, otherwise False."""
        act_str = f"{action} {str(parameters)}"
        for pattern in self.block_patterns:
            if pattern.search(act_str):
                return False
        return True
