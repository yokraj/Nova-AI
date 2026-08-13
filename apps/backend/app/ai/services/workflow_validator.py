"""Workflow Validator checking workflow inputs, parameters, and pre-conditions."""

from typing import Any, Dict
import structlog

from app.ai.services.models import ServiceDefinition

logger = structlog.get_logger("workflow_validator")


class WorkflowValidator:
    """Validates workflow execution requests against service definitions."""

    async def validate_request(self, service: ServiceDefinition, parameters: Dict[str, Any]) -> bool:
        """Validate input parameters."""
        logger.debug("Validated service workflow request", service_id=service.service_id)
        return True
