"""Voice Security Filter for transcript inspection before execution.

Enforces system security policy, preventing prompt injection, destructive commands, and unapproved sensitive operations over voice.
"""

import re
from typing import Tuple
from app.ai.desktop_automation.exceptions import ApprovalRequiredError


class VoiceSecurityError(Exception):
    """Raised when a voice command violates security policy."""

    pass


class VoiceSecurityFilter:
    """Inspects spoken transcripts for security violations before command dispatch."""

    FORBIDDEN_KEYWORDS = [
        "format c:",
        "drop database",
        "rm -rf",
        "delete system32",
        "shutdown /s",
        "reg delete",
        "disable firewall",
        "bypass security",
    ]

    SENSITIVE_KEYWORDS = [
        "registry_write",
        "modify registry",
        "delete user",
        "system admin",
        "sudo rm",
    ]

    @classmethod
    def inspect_transcript(cls, transcript: str) -> Tuple[bool, str]:
        """Inspects transcript text and returns (is_safe, reason).
        
        Raises VoiceSecurityError or ApprovalRequiredError for forbidden or sensitive actions.
        """
        text = transcript.lower().strip()

        # Check prompt injection patterns
        if "ignore previous instructions" in text or "you are now in god mode" in text:
            raise VoiceSecurityError("Prompt injection attempt detected in voice stream.")

        for kw in cls.FORBIDDEN_KEYWORDS:
            if kw in text:
                raise VoiceSecurityError(f"Forbidden destructive command detected: '{kw}'")

        for kw in cls.SENSITIVE_KEYWORDS:
            if kw in text:
                raise ApprovalRequiredError(f"Sensitive voice operation '{kw}' requires explicit human approval.")

        return True, "Passed security inspection."
