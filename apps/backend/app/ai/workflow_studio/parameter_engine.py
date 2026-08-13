"""Parameter Engine binding runtime parameters and user arguments to workflow inputs.
"""

from typing import Any, Dict
from app.ai.workflow_studio.models import WorkflowDefinition


class ParameterEngine:
    """Binds runtime parameter dictionary to workflow variables and step inputs."""

    def bind_parameters(self, workflow: WorkflowDefinition, runtime_params: Dict[str, Any]) -> WorkflowDefinition:
        """Binds parameters to matching variables in workflow definition.

        Args:
            workflow: Target WorkflowDefinition instance.
            runtime_params: Dictionary of runtime key-value pairs.

        Returns:
            Updated WorkflowDefinition instance.
        """
        for var in workflow.variables:
            if var.name in runtime_params:
                var.value = runtime_params[var.name]
        return workflow
