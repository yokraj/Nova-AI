"""Kernel Security Guard checking for sensitive operations requiring user approval.
"""

import re
from typing import Any, Dict
from app.ai.kernel.interfaces import ISecurityGuard


class KernelSecurityGuard(ISecurityGuard):
    """Enforces approval policy checkpoints for high-risk operations."""

    SENSITIVE_KEYWORDS = [
        "payment", "pay", "buy", "transfer", "bank", "credit_card",
        "delete", "remove", "wipe", "erase", "unlink", "drop_table",
        "install", "download_package", "apt-get", "pip_install", "setup.exe",
        "change_setting", "registry", "firewall", "system_config", "password",
        "send_email", "mail", "smtp", "dispatch_message",
        "government", "tax", "passport", "visa", "legal_submission",
    ]

    def check_approval_required(self, action_type: str, parameters: Dict[str, Any]) -> bool:
        """Determines if an action requires explicit user approval.

        Args:
            action_type: Category of action or natural language query.
            parameters: Action parameters.

        Returns:
            True if user approval is required.
        """
        combined = f"{action_type} {parameters.get('raw_query', '')} {str(parameters)}".lower()

        for kw in self.SENSITIVE_KEYWORDS:
            if kw in combined:
                return True

        if parameters.get("requires_approval") is True:
            return True

        return False

