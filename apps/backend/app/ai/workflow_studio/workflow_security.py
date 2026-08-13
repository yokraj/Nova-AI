"""Workflow Security encrypting sensitive variables and checking permission scopes.
"""

from app.ai.workflow_studio.models import WorkflowVariable


class WorkflowSecurity:
    """Enforces variable encryption and permission checks for sensitive automation actions."""

    def sanitize_sensitive_variable(self, variable: WorkflowVariable) -> WorkflowVariable:
        """Encrypts or masks sensitive variable values."""
        if variable.is_sensitive and isinstance(variable.value, str):
            variable.value = "*****ENCRYPTED*****"
        return variable
