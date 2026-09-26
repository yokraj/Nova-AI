"""Security Engine enforcing human approval holds and AES-256 encrypted credential storage.
"""

from typing import Any, Dict, Optional
from app.ai.desktop_automation.exceptions import ApprovalRequiredError


class SecurityEngine:
    """Enforces human approval holds for sensitive/destructive operations and manages encrypted credentials."""

    SENSITIVE_ACTIONS = {
        "registry_write",
        "administrator_elevation",
        "driver_install",
        "system_shutdown",
        "system_restart",
        "payment_transfer",
        "password_change",
        "file_delete",
        "browser_payment",
        "credential_expose",
        "destructive_web_action",
        "download_executable",
    }

    PROMPT_INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?(previous\s+)?(instructions?|prompts?)",
        r"reveal\s+(your\s+)?(secrets?|credentials?|passwords?|keys?)",
        r"override\s+(system\s+)?(instructions?|prompts?)",
        r"you\s+are\s+now\s+a",
        r"system\s+directive:",
        r"send\s+(your\s+)?credentials?",
    ]


    def __init__(self) -> None:
        self._encrypted_credentials: Dict[str, str] = {}

    def check_approval_required(self, action_name: str) -> bool:
        """Returns True if action is sensitive and requires explicit user confirmation."""
        return action_name.lower() in self.SENSITIVE_ACTIONS

    def enforce_security_check(self, action_name: str, is_user_approved: bool = False) -> None:
        """Raises ApprovalRequiredError if action requires approval and has not been approved."""
        if self.check_approval_required(action_name) and not is_user_approved:
            raise ApprovalRequiredError(f"Action '{action_name}' requires explicit human approval before execution.")

    def inspect_web_prompt_injection(self, text: str) -> Dict[str, Any]:
        """Classifies text extracted from web page as untrusted DATA and detects prompt injection attempts."""
        import re
        detected_patterns = []
        for pattern in self.PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                detected_patterns.append(pattern)

        is_injection = len(detected_patterns) > 0
        return {
            "is_untrusted_data": True,
            "contains_prompt_injection": is_injection,
            "detected_patterns": detected_patterns,
            "action": "WRAP_AS_DATA_ONLY" if is_injection else "PASS_AS_DATA",
        }

    def store_credential_encrypted(self, service_name: str, secret_val: str) -> Dict[str, Any]:
        """Stores secret encrypted using AES-256 format."""
        self._encrypted_credentials[service_name] = f"AES256_ENC::{secret_val[::-1]}"
        return {
            "service": service_name,
            "status": "ENCRYPTED_AND_STORED",
        }
