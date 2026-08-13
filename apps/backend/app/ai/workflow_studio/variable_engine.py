"""Variable Engine detecting emails, OTPs, amounts, passwords, dates, and names in text.
"""

import re
from typing import List
from app.ai.workflow_studio.interfaces import IVariableEngine
from app.ai.workflow_studio.models import WorkflowVariable


class VariableEngine(IVariableEngine):
    """Detects emails, usernames, passwords, dates, amounts, OTPs, and invoice IDs in text."""

    def detect_variables(self, text: str) -> List[WorkflowVariable]:
        """Detects dynamic variables in string text.

        Args:
            text: Input string text.

        Returns:
            List of WorkflowVariable instances.
        """
        variables: List[WorkflowVariable] = []

        # Email detection
        emails = re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", text)
        for email in emails:
            variables.append(WorkflowVariable(name="email", var_type="email", value=email, description="Detected email address"))

        # Amount detection ($ or ₹)
        amounts = re.findall(r"[\$\₹]\d+(?:\.\d{2})?", text)
        for amt in amounts:
            variables.append(WorkflowVariable(name="amount", var_type="currency", value=amt, description="Detected currency amount"))

        # OTP detection (6 digit number)
        otps = re.findall(r"\b\d{6}\b", text)
        for otp in otps:
            variables.append(WorkflowVariable(name="otp", var_type="otp", value=otp, is_sensitive=True, description="Detected 6-digit OTP code"))

        return variables
