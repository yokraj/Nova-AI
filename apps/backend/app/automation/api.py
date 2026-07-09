"""FastAPI API routes mapping Workflow lifecycles operations.

Exposes endpoints to create workflows, trigger executions,
inspect history events, and submit cancellation requests.
"""

from typing import Any, Dict
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.automation.models import Workflow, WorkflowResult
from app.automation.services import WorkflowService
from app.core.dependency_container import resolve

router = APIRouter(prefix="/workflows", tags=["workflows"])


class ExecuteWorkflowRequest(BaseModel):
    """Payload representing startup variables variables mapping passed to execution."""

    variables: Dict[str, Any] = Field(
        default_factory=dict,
        description="Variables dictionary values context maps.",
    )


@router.post(
    "/", response_model=Workflow, status_code=status.HTTP_201_CREATED
)
def create_workflow(payload: Workflow) -> Any:
    """Creates a new workflow configuration schema in memory."""
    service = resolve(WorkflowService)
    try:
        return service.create_workflow(payload)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
        )


@router.post("/{id}/execute", response_model=WorkflowResult)
async def execute_workflow(id: str, payload: ExecuteWorkflowRequest) -> Any:
    """Triggers workflow execution task flow."""
    service = resolve(WorkflowService)
    try:
        return await service.execute_workflow(id, payload.variables)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
        )


@router.get("/{id}/status")
def get_workflow_status(id: str) -> Any:
    """Inspects the current workflow execution status state."""
    service = resolve(WorkflowService)
    workflow = service.get_workflow(id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow with ID '{id}' not found.",
        )
    return {"id": workflow.id, "status": workflow.status}


@router.get("/{id}/history")
def get_workflow_history(id: str) -> Any:
    """Retrieves step transition events history logs list."""
    service = resolve(WorkflowService)
    context = service.get_context(id)
    if not context:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow context log for '{id}' not found.",
        )
    return context.history


@router.post("/{id}/cancel")
async def cancel_workflow(id: str) -> Any:
    """Requests active workflow execution task cancellation."""
    service = resolve(WorkflowService)
    workflow = service.get_workflow(id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow with ID '{id}' not found.",
        )
    await service.cancel_workflow(id)
    return {"id": id, "status": "cancellation_requested"}
